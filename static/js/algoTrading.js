$(document).on("click","#webhookStatus",function(){
    var webhookStatus = $("#webhookStatus").prop("checked");
    var nameMap = {"true":"Enabled","false":"Disabled"};
        $.get("/settoggle/"+webhookStatus);

});
$(document).on("click",function(event){
    var idOfTarget = event.target.id;
    if(idOfTarget == "CE" || idOfTarget == "PE"|| idOfTarget == "exitOrder")
    {
        var httpMap = {"CE":"/buy/manual",    "PE":"/sell/manual",    "exitOrder":"/exit/manual"};
        $.get(httpMap[idOfTarget]);
    }

});
