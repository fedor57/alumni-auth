$(function () {
    $(".alumni-select").autocomplete({
        source: "/api/get_alumni/",
        minLength: 2,
        select: function(event, ui) {
            $('.invitee-id').val(ui.item.id);
        }
    });
});
