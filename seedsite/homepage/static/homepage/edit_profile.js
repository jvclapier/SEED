// The change event is fired when a form element loses focus
// and its value has changed since the last time we interacted with it
$(function(){
    $('#id_current_password').change(function() {
        console.log("current_password has been changed");
        // If the element *has* a value
        if ($(this).val()) {
            $('#id_new_password').attr('disabled', false);
            $('#id_confirm_new_password').attr('disabled', false);
        }
        // If the element doesn't have a value
        else {
            // Clear the value of all next steps and disable
            $('#id_new_password').val('');
            $('#id_new_password').attr('disabled', true);
            $('#id_confirm_new_password').val('');
            $('#id_confirm_new_password').attr('disabled', true);
        }
    });

    $('#id_current_password').keydown(function(event) {
        // If they pressed tab AND the input has a (valid) value
        if ($(this).val() && event.keyCode == 9) {
            $('#id_new_password').attr('disabled', false);
            $('#id_confirm_new_password').attr('disabled', false);
        }
    });
});
