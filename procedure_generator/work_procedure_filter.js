var textFieldValue = this.getField("WORK_PROCEDURE_FILTER").value.trim();
var source_field = this.getField("WORK_PROCEDURE_SELECT_ALL");
var select_field = this.getField("WORK_PROCEDURE_SELECT");

// Normalize the filter text just once: remove non-alphabetic characters, make lowercase
var normalizedFilter = textFieldValue.replace(/[^a-zA-Z]/g, '').toLowerCase();

// function to check if an option matches the filter
function optionMatchesFilter(option, filterText) {
    // Ensure the option is a string, then normalize it: 
    // remove non-alphabetic characters, make lowercase
    var normalizedOption = option.replace(/[^a-zA-Z]/g, '').toLowerCase();
    
    // Check if the normalized option contains the normalized filter text using indexOf
    return normalizedOption.indexOf(filterText) !== -1;
}

// Clear the dropdown
select_field.clearItems();

// Loop through source items, filter (if necessary), and add to the dropdown
for (var i = 0, j = 0; i < source_field.numItems; i++) {
    var option = source_field.getItemAt(i, false);
    if (textFieldValue.length === 0 || optionMatchesFilter(option, normalizedFilter)) {
        select_field.insertItemAt(option, option, j++);
    }
}