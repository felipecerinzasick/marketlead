$(document).ready(function () {
    $('[data-toggle="tooltip"]').each(function (i, el) {
        $(el).tooltip({'placement': $(el).attr('data-placement')})
    });
});