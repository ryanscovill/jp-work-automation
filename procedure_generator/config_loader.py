import os
import sys
import yaml
from typing import Any, Dict, Optional

class ConfigLoader:
    _instance: Optional['ConfigLoader'] = None
    _config: Optional[Dict[str, Any]] = None
    
    def __new__(cls, config_file: str = "swp_config.yaml") -> 'ConfigLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_file)
        return cls._instance
    
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


config = ConfigLoader()


def get_default_template_folder() -> str:
    return config.get("paths.default_template_folder", "")

def get_default_work_procedure_folder() -> str:
    return config.get("paths.default_work_procedure_folder", "")

def get_browser_path() -> str:
    return config.get("paths.browser_path", "")

def get_worksafe_bc_url() -> str:
    return config.get("worksafe_bc.url", "")

def get_template_select_field() -> str:
    return config.get("field_names.template_select_field", "TEMPLATE_SELECT")

def get_work_procedure_select_field() -> str:
    return config.get("field_names.work_procedure_select_field", "WORK_PROCEDURE_SELECTX")

def get_work_procedure_select_all_field() -> str:
    return config.get("field_names.work_procedure_select_all_field", "WORK_PROCEDURE_SELECT_ALL")

def get_work_procedure_text_field() -> str:
    return config.get("field_names.work_procedure_text_field", "SWPX")

def get_num_work_procedure_fields() -> int:
    return config.get("field_names.num_work_procedure_fields", 12)