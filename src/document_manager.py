"""Document manager module."""

import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium_core.waits import wait_and_click, wait_and_send_keys, wait_for_element, retry_on_exception
from selenium_core.logger import get_logger
from selenium_core.exceptions import ProcessingError

logger = get_logger(__name__)


class DocumentManager:
    """Manages document assignment to departments."""
    
    def __init__(self, driver: Chrome):
        """
        Initialize document manager.
        
        Args:
            driver: Chrome WebDriver instance
        """
        self.driver = driver
    
    @retry_on_exception(max_attempts=3, delay=2.0)
    def assign_document_to_department(
        self,
        department_index: int,
        department_name: str,
        document_name: str
    ) -> None:
        """
        Assign a document to a department.
        
        Args:
            department_index: Department row index
            department_name: Department name (for logging)
            document_name: Document to assign
            
        Raises:
            ProcessingError: If assignment fails
        """
        try:
            logger.info(f"Processing department {department_index}: {department_name}")
            
            # Click edit button
            self._click_edit_button(department_index)
            
            # Search and select document
            self._search_and_select_document(document_name)
            
            # Update permissions and save
            self._update_and_save()
            
            # Wait for modal to close
            self._wait_for_modal_close()
            
            logger.info(f"✓ Successfully processed {department_name}")
            
        except Exception as e:
            logger.error(f"Failed to process department {department_index}: {e}")
            raise ProcessingError(f"Document assignment failed: {e}") from e
    
    def _click_edit_button(self, department_index: int) -> None:
        """Click the edit button for a department."""
        edit_xpath = f'//*[@id="def-table"]/tbody/tr[{department_index}]/td[4]/a[1]'
        edit_button = wait_for_element(
            self.driver,
            By.XPATH,
            edit_xpath,
            timeout=10,
            condition='clickable'
        )
        
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            edit_button
        )
        edit_button.click()
        time.sleep(1)
    
    def _search_and_select_document(self, document_name: str) -> None:
        """Search for and select a document."""
        time.sleep(1)
        
        # Search for document
        wait_and_send_keys(
            self.driver,
            By.XPATH,
            '//*[@id="find-categories-text"]',
            document_name,
            timeout=10
        )
        time.sleep(1)
        
        # Select document (using specific checkbox)
        # Note: The index 730 is hardcoded in original - might need adjustment
        wait_and_click(
            self.driver,
            By.XPATH,
            '//*[@id="list-categories"]/li[730]/label/input',
            timeout=10
        )
        time.sleep(1)
    
    def _update_and_save(self) -> None:
        """Update permissions and save changes."""
        # Click update permissions
        wait_and_click(
            self.driver,
            By.ID,
            'UpdateUsersPermissions',
            timeout=10
        )
        
        # Click save
        wait_and_click(
            self.driver,
            By.ID,
            'send-edit-department',
            timeout=10
        )
    
    def _wait_for_modal_close(self) -> None:
        """Wait for processing modal to appear and disappear."""
        # Wait for loading indicator to appear
        try:
            wait_for_element(
                self.driver,
                By.XPATH,
                '//*[@id="box-edit-department"]/div/div/div[2]/div[1]',
                timeout=10,
                condition='presence'
            )
        except:
            pass
        
        # Wait for loading indicator to disappear
        try:
            wait_for_element(
                self.driver,
                By.XPATH,
                '//*[@id="box-edit-department"]/div/div/div[2]/div[1]',
                timeout=10,
                condition='invisible'
            )
        except:
            pass
        
        time.sleep(1)
        
        # Close modal
        try:
            close_button = wait_for_element(
                self.driver,
                By.XPATH,
                '//*[@id="box-edit-department"]/div/div/div[1]/button',
                timeout=10,
                condition='clickable'
            )
            close_button.click()
            time.sleep(1)
        except Exception as e:
            logger.warning(f"Could not close modal: {e}")
