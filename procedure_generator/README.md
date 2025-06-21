# Safe Work Procedure Generator

Takes a work order and creates a safe work procedure PDF from a template and procedure documents.

## Development 

`pip install -r requirements.txt`


## Building

To make an executable

`PLAYWRIGHT_BROWSERS_PATH="0"`
`playwright uninstall`

`pyinstaller script.spec --clean`