document.addEventListener("DOMContentLoaded", function(){

    const toggleBtn = document.getElementById("themeToggle");

    if(localStorage.getItem("theme") === "light"){
        document.body.classList.add("light-mode");
        if(toggleBtn){
            toggleBtn.innerHTML = "☀️";
        }
    }

    if(toggleBtn){
        toggleBtn.addEventListener("click", function(){

            document.body.classList.toggle("light-mode");

            if(document.body.classList.contains("light-mode")){
                localStorage.setItem("theme","light");
                toggleBtn.innerHTML = "☀️";
            }
            else{
                localStorage.setItem("theme","dark");
                toggleBtn.innerHTML = "🌙";
            }

        });
    }

});