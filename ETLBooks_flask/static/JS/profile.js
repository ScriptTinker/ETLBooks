document.addEventListener("DOMContentLoaded",function(){
    const edit_profile_btn = document.getElementById("edit_profile_btn")
    const edit_profile_frame = document.getElementById("edit_profile_frame")

    edit_profile_btn.addEventListener("click", function(){
        edit_profile_frame.style.display = "block";
    })
}
)