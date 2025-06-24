function validatePassword(){
    var oldpassword = $("#dzpassword").val();
    var newpassword = $("#dz-con-password").val();
    var confirmpassword = $("#dz-old-password").val();
    if(oldpassword=="" || newpassword=="" || confirmpassword==""){
       return false;
    }
    
 }
    $("#send-otp").click(function (el) {
       $.ajax({
            type: "POST",
            url: "{% url 'mophy:send_otp' %}",
            data: {
              csrfmiddlewaretoken: "{{ csrf_token }}",
            },
            success: function (data) {
             $("#verify-otp").show();
            },
          })
       });
 
       $("#verify-otp").click(function (el) {
          var otp = $("#otp").val();
       $.ajax({
            type: "POST",
            url: "{% url 'mophy:send_otp' %}",
            data: {
              csrfmiddlewaretoken: "{{ csrf_token }}",
              otp:otp
            },
            success: function (data) {
           if(data.success){
             $("#change_password").show();
             $("#verify-otp").hide();
           }
           else{
             $("#change_password").hide();
           }
            },
          })
       });