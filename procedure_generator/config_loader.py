import os
import sys
import yaml
from typing import Any, Dict, Optional

class ConfigSection:
    """Helper class to provide dot notation access to configuration sections"""
    def __init__(self, config_dict: Dict[str, Any], defaults: Optional[Dict[str, Any]] = None):
        self._config = config_dict
        self._defaults = defaults or {}
        
    def __getattr__(self, name: str) -> Any:
        if name in self._config:
            return self._config[name]
        elif name in self._defaults:
            return self._defaults[name]
        else:
            raise AttributeError(f"Configuration key '{name}' not found")

class ConfigLoader:
    _instance: Optional['ConfigLoader'] = None
    _config: Optional[Dict[str, Any]] = None
    
    def __new__(cls, config_file: str = "swp_config.yaml") -> 'ConfigLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_file)
            cls._instance._setup_sections()
        return cls._instance
    
    def _setup_sections(self) -> None:
        """Setup configuration sections with defaults"""
        if self._config is None:
            return
            
        # Define defaults for each section
        path_defaults = {
            "default_template_folder": "",
            "default_work_procedure_folder": "",
            "browser_path": ""
        }
        
        field_name_defaults = {
            "template_select_field": "TEMPLATE_SELECT",
            "work_procedure_select_field": "WORK_PROCEDURE_SELECTX",
            "work_procedure_select_all_field": "WORK_PROCEDURE_SELECT_ALL",
            "work_procedure_text_field": "SWPX",
            "num_work_procedure_fields": 12
        }
        
        timeout_defaults = {
            "field_interaction_delay": 50,
            "short_timeout": 300,
            "standard_timeout": 1000,
            "navigation_timeout": 500,
            "content_change_threshold": 500,
            "next_button_check_interval": 5,
            "periodic_page_check_interval": 10
        }
        
        ui_defaults = {
            "viewport_width": 1400,
            "viewport_height": 900
        }
        
        worksafe_bc_defaults = {
            "url": "https://prevnop.online.worksafebc.com/"
        }
        
        # Create ConfigSection instances with defaults
        self.paths = ConfigSection(self._config.get("paths", {}), path_defaults)
        self.field_names = ConfigSection(self._config.get("field_names", {}), field_name_defaults)
        self.timeouts = ConfigSection(self._config.get("timeouts", {}), timeout_defaults)
        self.ui_settings = ConfigSection(self._config.get("ui_settings", {}), ui_defaults)
        self.worksafe_bc = ConfigSection(self._config.get("worksafe_bc", {}), worksafe_bc_defaults)
        self.nop = ConfigSection(self._config.get("NOP", {}))
    
    def _load_config(self, config_file: str) -> None:
        # Determine the directory of the executable
        # sys.argv[0] gives the path used to invoke the script/exe
        # os.path.abspath ensures it's a full path
        # os.path.dirname gets the directory
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        # Construct the full path to the config file in the exe's directory
        config_path = os.path.join(exe_dir, config_file)
        
        # Check if config file exists, if not try one directory up
        if not os.path.exists(config_path):
            parent_dir = os.path.dirname(exe_dir)
            config_path = os.path.join(parent_dir, config_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in configuration file '{config_file}': {e}")
            
    def get(self, key_path: str, default: Any = None) -> Any:
        if self._config is None:
            return default
            
        keys = key_path.split('.')
        current = self._config
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_paths(self) -> Dict[str, str]:
        return self.get("paths", {})
    
    def get_debug_paths(self) -> Dict[str, str]:
        return self.get("debug_paths", {})
    
    def get_timeouts(self) -> Dict[str, int]:
        return self.get("timeouts", {})
    
    def get_ui_settings(self) -> Dict[str, Any]:
        return self.get("ui_settings", {})
    
    def get_field_names(self) -> Dict[str, Any]:
        return self.get("field_names", {})
    
    def get_worksafe_bc_config(self) -> Dict[str, str]:
        return self.get("worksafe_bc", {})
    
    def get_nop_config(self) -> Dict[str, Any]:
        return self.get("NOP", {})
    
    def reload(self, config_file: str = "swp_config.yaml") -> None:
        self._load_config(config_file)
        self._setup_sections()
        
config = ConfigLoader()