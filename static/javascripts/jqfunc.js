// Выделение пунктов меню при наведении
$(".top-menu li:not(.active)").mouseenter(function () {
    $(this).addClass("active");
}).mouseleave(function () {
    $(this).removeClass("active");
});
// Анимация изображений при наведении
$("figure img").hover(
function() {
    $(this).animate({
        width: "350px",      
    }, "slow");
}, function() {
    $(this).animate({
        width: "320px",  
    }, "slow");
});