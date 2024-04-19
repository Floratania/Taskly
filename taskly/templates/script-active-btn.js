<script>
    $(document).ready(function(){
        var activeButton = sessionStorage.getItem('activeButton');
    
       
  
    
        if(activeButton && activeButton !== '{% url "password_reset" %}' ) {
          $("a[href='" + activeButton + "']").addClass("active");
        }
  
    
    
        $(".navbar-btn").click(function(){
            $(".navbar-btn").removeClass("active");
            $(this).addClass("active");
            sessionStorage.setItem('activeButton', $(this).attr('href'));
        });
    });
    </script>