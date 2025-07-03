import sys
import yaml
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class PathsConfig(BaseModel):
    default_template_folder: str = ""
    default_work_procedure_folder: str = ""
    browser_path: str = ""


class DebugPathsConfig(BaseModel):
    source_pdf: str = ""
    template_folder: str = ""
    work_procedure_folder: str = ""


class FieldNamesConfig(BaseModel):
    template_select_field: str = "TEMPLATE_SELECT"
    work_procedure_select_field: str = "WORK_PROCEDURE_SELECTX"
    work_procedure_select_all_field: str = "WORK_PROCEDURE_SELECT_ALL"
    work_procedure_text_field: str = "SWPX"
    num_work_procedure_fields: int = 12


class TimeoutsConfig(BaseModel):
    field_interaction_delay: int = 50
    short_timeout: int = 300
    standard_timeout: int = 1000
    navigation_timeout: int = 500
    content_change_threshold: int = 500
    next_button_check_interval: int = 5
    periodic_page_check_interval: int = 10


class UISettingsConfig(BaseModel):
    default_window_size: List[int] = Field(default=[800, 600])
    viewport_width: int = 1400
    viewport_height: int = 900


class WorksafeBCConfig(BaseModel):
    url: str = "https://prevnop.online.worksafebc.com/"


class NOPConfig(BaseModel):
    transformations: Dict[str, Any] = Field(default_factory=dict)
    pages: List[Dict[str, Any]] = Field(default_factory=list)


class ExcelToPDFProcessingConfig(BaseModel):
    default_sheet_name: str = ""


class FieldMappingConfig(BaseModel):
    pdf_field: str
    type: str = "text"


class ExcelToPDFConfig(BaseModel):
    field_mappings: Dict[str, FieldMappingConfig] = Field(default_factory=dict)
    processing: ExcelToPDFProcessingConfig = Field(default_factory=ExcelToPDFProcessingConfig)


class Config(BaseSettings):
    model_config = {"extra": "allow"}
    
    paths: PathsConfig = Field(default_factory=PathsConfig)
    debug_paths: DebugPathsConfig = Field(default_factory=DebugPathsConfig)
    field_names: FieldNamesConfig = Field(default_factory=FieldNamesConfig)
    timeouts: TimeoutsConfig = Field(default_factory=TimeoutsConfig)
    ui_settings: UISettingsConfig = Field(default_factory=UISettingsConfig)
    worksafe_bc: WorksafeBCConfig = Field(default_factory=WorksafeBCConfig)
    nop: NOPConfig = Field(default_factory=NOPConfig, alias="NOP")
    excel_to_pdf: ExcelToPDFConfig = Field(default_factory=ExcelToPDFConfig, alias="EXCEL_TO_PDF")

    def __init__(self, **kwargs):
        # Load YAML config and merge with kwargs
        config_data = self._load_yaml_config()
        super().__init__(**config_data, **kwargs)

    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load YAML configuration file"""
        config_file = self._find_config_file("swp_config.yaml")
        if not config_file:
            raise FileNotFoundError("Configuration file 'swp_config.yaml' not found.")
        
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except (FileNotFoundError, yaml.YAMLError):
            raise FileNotFoundError("Failed to load configuration file 'swp_config.yaml'.")

    def _find_config_file(self, filename: str) -> Path | None:
        """Find config file in various locations"""
        search_paths = [
            # Current working directory
            Path.cwd() / "procedure_generator" / filename,
            # Executable directory
            Path(sys.argv[0]).resolve().parent / filename,
            # Parent directory of executable
            Path(sys.argv[0]).resolve().parent.parent / filename,
            # Same directory as this config_loader.py file
            Path(__file__).resolve().parent / filename,
            # Current working directory
            Path.cwd() / filename,
        ]
        
        for config_path in search_paths:
            if config_path.exists():
                return config_path
        
        return None


# Create global config instance
try:
    config = Config()
except FileNotFoundError as e:
    print(f"Error loading configuration: {e}")
    input("Press Enter to exit...")
    sys.exit(1)
