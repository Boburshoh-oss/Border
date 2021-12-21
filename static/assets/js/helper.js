$(document).ready(function () {
    $.ajax({
        type: 'get',
        url: '/datahome/',
        success: function (data) {
            console.log(data);
        }
    });
});