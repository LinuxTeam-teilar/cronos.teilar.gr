$(document).ready(function() {
    $("#sidebar li.sidebar_head").click(function() {
        $(this).next("div.sidebar_body").slideToggle(300).siblings("div.sidebar_body").slideUp('slow');
        $(this).siblings();
    });
});
