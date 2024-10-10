function download()
{
    var url=document.getElementById("linn").value;
    document.getElementById("linn").setAttribute("placeholder","正在下载，请稍等...");
    document.getElementById("linn").value = "";

    $.ajax({
        url:'download/',
        type: "GET",
        data:{
            'url':url,
            // Forbidden（CSRF）方法：加上下面这一句
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
        },
        success:function(data){
            alert("下载成功！")
            document.getElementById("linn").setAttribute("placeholder","请输入下载链接");
        },
        error:function(data){
            alert("下载失败！")
            document.getElementById("linn").setAttribute("placeholder","请输入下载链接");
        }
    })
}