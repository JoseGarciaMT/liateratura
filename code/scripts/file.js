<!DOCTYPE html>
<html lang="en" class="cuento_page">


<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script type="text/javascript">

        function flash() {
          $("#cont_story_rules").show().fadeOut("slow");
        }
        $("#rules_button").on("click", function() {
          $( "body" )
            .on("click", "#cont_story_rules", flash)
            .find( "#cont_story_rules" )
              .css("opacity", "1");
        });
        $("#rules_button").on("click", function() {
          $("body")
            .off("click", "#cont_story_rules", flash)
            .find("#cont_story_rules")
              .css("opacity", "0");
        });



        const rul_button = document.getElementById("rules_button");
        const tru_button = document.getElementById("truchi_btn");
        
        rul_button.onclick = function () {
            const myrules = document.querySelector("#cont_story_rules");
            myrules.style.opacity = 1;
           };
           
        tru_button.onclick = function () {
            const tru_card = document.querySelector("#truchicard");
            tru_card.style.opacity = 1;
           };
           

        rul_button.onmouseleave = function () {
            var myrules = document.getElementById("cont_story_rules");
            myrules.style.opacity = 0;
           };
                   
                   
        tru_button.onclick = function () {
            tru_card.style.opacity = 1;
           };
           
        $('#truchicard').click(function(e) {
            e.stopPropagation();
            $('#truchicard').fadeOut(300);
        });
        
        $.fn.clickOff = function(callback, selfDestroy) {
            var clicked = false;
            var parent = this;
            var destroy = selfDestroy || true;
        
            parent.click(function() {
                clicked = true;
            });
        
            $(document).click(function(event) {
                if (!clicked && parent.is(':visible')) {
                    if (callback) callback.call(parent, event)
                }
                if (destroy) {
                    parent.off("clickOff");
                }
                clicked = false;
            });
        };
        
        $("#truchi_btn").clickOff(function() {
            $('#truchicard').fadeOut(300);
        });
        
        $("#rules_button").clickOff(function() {
            $('#cont_story_rules').fadeOut(300);
        });
        

        document.addEventListener((e) => {
          if (!e.target.classList.contains("#truchi_btn")) {
            $("#truchicard").close();
            }
          }
        
        
        
        function getStory() {
           var story = document.getElementById("raw_story").innerHTML;
           var title = document.getElementById("story_title_block").innerHTML;

           document.getElementById("downl_story_form").setAttribute("value", story);
           document.getElementById("downl_title_form").setAttribute("value", title);
        }
</script>
