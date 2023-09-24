// Set this javascript in the WORK_PROCEDURE_FILTER field's Blur action

var textFieldValue = this.getField("WORK_PROCEDURE_FILTER").value;
var source_field = this.getField("WORK_PROCEDURE_SELECT_ALL");
var select_field = this.getField("WORK_PROCEDURE_SELECT");

// function to filter the options based on text
function filterOptions(optionsList, filterText) {
    // Normalize the filter text: remove non-alphabetic characters, make lowercase
    var normalizedFilter = filterText.replace(/[^a-zA-Z]/g, '').toLowerCase();

    // Filter function
    var filtered = optionsList.filter(function(option) {
        // Ensure the option is a string, then normalize it: 
        // remove non-alphabetic characters, make lowercase
        var normalizedOption = option.replace(/[^a-zA-Z]/g, '').toLowerCase();

        // Check if the normalized option contains the normalized filter text using indexOf
        return normalizedOption.indexOf(normalizedFilter) !== -1;
    });

    return filtered;
}

// get all the options
var optionsFromSource = [];
for (var i = 0; i < source_field.numItems; i++) {
    optionsFromSource.push(source_field.getItemAt(i, false));
}

// filter the options based on the search field
var filteredOptions = [];
textFieldValue = textFieldValue.trim();
if(textFieldValue.length > 0) {
    filteredOptions = filterOptions(optionsFromSource, textFieldValue);
} else {
    filteredOptions = optionsFromSource;
}

// Clear the dropdown
select_field.clearItems();

// Add filtered options to the dropdown
for (var i = 0; i < filteredOptions.length; i++) {
    select_field.insertItemAt(filteredOptions[i], filteredOptions[i], i);
}