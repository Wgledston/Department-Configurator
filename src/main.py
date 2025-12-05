"""Main entry point for Department Configurator."""

import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium_core import BrowserManager, QuestorAuth, get_logger
from selenium_core.waits import wait_and_send_keys, wait_and_click, wait_for_element
from selenium_core.exceptions import SeleniumAutomationError
from .config import settings
from .department_service import DepartmentService
from .document_manager import DocumentManager


logger = get_logger(__name__, log_dir=settings.LOGS_DIR)


def setup_page(driver: Chrome) -> None:
    """Setup the page by searching and adjusting page size."""
    # Search for departments
    logger.info(f"Searching for departments: {settings.DEPARTMENT_SEARCH}")
    wait_and_send_keys(
        driver,
        By.XPATH,
        '//*[@id="search-name-direct"]',
        settings.DEPARTMENT_SEARCH
    )
    time.sleep(2)
    
    # Set page size to show all results
    logger.info("Adjusting page size to show all results")
    try:
        wait_and_click(
            driver,
            By.XPATH,
            '//*[@id="pageSize"]/option[9]',
            timeout=10
        )
    except Exception as e:
        logger.warning(f"Could not adjust page size: {e}")
    
    # Wait for table to load
    wait_for_element(driver, By.ID, 'def-table', timeout=10)
    
    # Wait for loading indicator to disappear
    try:
        wait_for_element(
            driver,
            By.XPATH,
            '//*[@id="def-table_processing"]/div[2]/div',
            timeout=10,
            condition='invisible'
        )
    except:
        pass


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Department Configurator - Starting")
    logger.info("=" * 60)
    
    driver = None
    
    try:
        # Create browser
        logger.info("Initializing browser...")
        driver = BrowserManager.create_driver(
            headless=settings.HEADLESS,
            window_size=settings.WINDOW_SIZE,
            chrome_binary=settings.CHROME_BINARY,
            block_images=settings.BLOCK_IMAGES
        )
        
        # Login
        logger.info("Authenticating...")
        QuestorAuth.login(
            driver,
            settings.APP_URL,
            settings.APP_USERNAME,
            settings.APP_PASSWORD
        )
        
        # Setup page
        setup_page(driver)
        
        # Initialize services
        dept_service = DepartmentService(driver)
        doc_manager = DocumentManager(driver)
        
        # List departments
        logger.info("Loading departments...")
        departments = dept_service.list_departments()
        
        if not departments:
            logger.warning("No departments found")
            return
        
        logger.info(f"Found {len(departments)} departments")
        
        # Prompt for exclusions
        departments = dept_service.prompt_for_exclusions(departments)
        
        # Process departments
        logger.info("Starting department processing...")
        processed = 0
        failed = 0
        skipped = 0
        
        for dept in departments:
            if not dept.should_process:
                logger.info(f"⏭️ Skipping department {dept.index}: {dept.name}")
                skipped += 1
                continue
            
            try:
                doc_manager.assign_document_to_department(
                    dept.index,
                    dept.name,
                    settings.DOCUMENT_NAME
                )
                processed += 1
            except Exception as e:
                logger.error(f"Failed to process {dept.name}: {e}")
                failed += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("Department Configurator - Completed")
        logger.info(f"✅ Processed: {processed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⏭️ Skipped: {skipped}")
        logger.info("=" * 60)
        
    except SeleniumAutomationError as e:
        logger.error(f"Automation error: {e}")
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    
    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
