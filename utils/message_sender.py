"""
Connection and message handling utilities for LINE Bot
Handles connection timeouts and message delivery failures
"""

import time
import logging
from typing import Optional, List, Tuple
from linebot.v3.messaging import (
    ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)

logger = logging.getLogger(__name__)

class RobustMessageSender:
    """Handles robust message sending with timeout and retry logic"""
    
    def __init__(self, line_bot_api: MessagingApi):
        self.line_bot_api = line_bot_api
        self.max_message_length = 1900  # Safe limit to prevent timeouts
        self.retry_attempts = 3
        self.base_timeout = 5.0  # seconds
        
    def send_reply_with_timeout(self, reply_token: str, message: str, 
                               max_retries: int = 3) -> Tuple[bool, Optional[str]]:
        """
        Send reply message with timeout handling and retries
        
        Args:
            reply_token: LINE reply token
            message: Message text to send
            max_retries: Maximum retry attempts
            
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        # Truncate message if too long
        if len(message) > self.max_message_length:
            message = message[:self.max_message_length - 50] + "\n\n... (ข้อความถูกตัดเนื่องจากยาวเกินไป)"
            logger.warning(f"Message truncated to {len(message)} characters")
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                
                self.line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[TextMessage(text=message)]
                    )
                )
                
                elapsed_time = time.time() - start_time
                logger.info(f"Reply sent successfully in {elapsed_time:.2f}s (attempt {attempt + 1}): {message[:50]}...")
                return True, None
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Send attempt {attempt + 1} failed: {e}")
                
                # If this is a connection reset or timeout, wait before retry
                if "Connection reset" in str(e) or "timeout" in str(e).lower():
                    if attempt < max_retries - 1:  # Don't sleep on last attempt
                        sleep_time = self.base_timeout * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Waiting {sleep_time}s before retry...")
                        time.sleep(sleep_time)
                        continue
                
                # For other errors, don't retry
                break
        
        # All attempts failed
        logger.error(f"Failed to send reply after {max_retries} attempts: {last_error}")
        return False, last_error
    
    def send_fallback_message(self, reply_token: str) -> bool:
        """Send a simple fallback error message"""
        try:
            fallback_message = "❌ เกิดข้อผิดพลาดในการส่งข้อความ กรุณาลองใหม่อีกครั้ง"
            
            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=fallback_message)]
                )
            )
            logger.info("Fallback message sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send fallback message: {e}")
            return False

class MessageQueue:
    """Handles queued message sending for multi-step operations"""
    
    def __init__(self, sender: RobustMessageSender):
        self.sender = sender
        self.queue: List[Tuple[str, str]] = []  # (reply_token, message)
        
    def add_message(self, reply_token: str, message: str):
        """Add message to queue"""
        self.queue.append((reply_token, message))
        
    def send_all(self, delay_between: float = 1.0) -> Tuple[int, int]:
        """
        Send all queued messages with delays
        
        Args:
            delay_between: Delay between messages in seconds
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        successful = 0
        failed = 0
        
        for i, (reply_token, message) in enumerate(self.queue):
            # Add delay between messages (except first)
            if i > 0:
                time.sleep(delay_between)
                
            success, error = self.sender.send_reply_with_timeout(reply_token, message)
            
            if success:
                successful += 1
            else:
                failed += 1
                # Send fallback for failed messages
                self.sender.send_fallback_message(reply_token)
        
        # Clear queue after sending
        self.queue.clear()
        
        logger.info(f"Message queue processed: {successful} successful, {failed} failed")
        return successful, failed

def create_connection_aware_sender(line_bot_api: MessagingApi) -> RobustMessageSender:
    """Factory function to create a robust message sender"""
    return RobustMessageSender(line_bot_api)