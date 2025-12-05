"""Department service module."""

from dataclasses import dataclass
from typing import List
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium_core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Department:
    """Represents a department."""
    index: int
    name: str
    should_process: bool = True


class DepartmentService:
    """Service for managing departments."""
    
    def __init__(self, driver: Chrome):
        """
        Initialize department service.
        
        Args:
            driver: Chrome WebDriver instance
        """
        self.driver = driver
    
    def list_departments(self) -> List[Department]:
        """
        Extract list of departments from table.
        
        Returns:
            List of Department objects
        """
        rows = self.driver.find_elements(By.XPATH, '//table[@id="def-table"]/tbody/tr')
        departments = []
        
        for index, row in enumerate(rows, start=1):
            try:
                name_element = row.find_element(By.XPATH, './td[1]')
                name = name_element.text
                departments.append(Department(index, name))
                logger.info(f"{index} - {name}")
            except Exception as e:
                logger.error(f"Error processing row {index}: {e}")
        
        return departments
    
    def prompt_for_exclusions(self, departments: List[Department]) -> List[Department]:
        """
        Prompt user to select departments to exclude from processing.
        
        Args:
            departments: List of departments
            
        Returns:
            Updated list with should_process flags
        """
        print("\n" + "="*60)
        print("DEPARTMENT SELECTION")
        print("="*60)
        
        remove = input("Do you want to exclude any departments? (y/n): ").strip().lower()
        
        while remove not in ('y', 'n'):
            remove = input("Invalid option. Type 'y' for yes or 'n' for no: ").strip().lower()
        
        if remove == 'n':
            return departments
        
        indices_to_remove = []
        print("\nEnter department numbers to exclude (0 to finish):")
        
        while True:
            line = input("Department number: ").strip()
            if line == '0':
                break
            
            try:
                idx = int(line)
                if 1 <= idx <= len(departments):
                    indices_to_remove.append(idx)
                    print(f"✓ Department {idx} ({departments[idx-1].name}) marked for exclusion")
                else:
                    print(f"Please enter a number between 1 and {len(departments)}")
            except ValueError:
                print("Invalid input - please enter a number")
        
        # Mark departments for exclusion
        for idx in indices_to_remove:
            departments[idx-1].should_process = False
        
        # Show summary
        excluded = [d.name for d in departments if not d.should_process]
        to_process = [d.name for d in departments if d.should_process]
        
        print("\n" + "="*60)
        print(f"Departments to process: {len(to_process)}")
        print(f"Departments excluded: {len(excluded)}")
        print("="*60 + "\n")
        
        return departments
