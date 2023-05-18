let statuses = document.getElementsByClassName("status");
for(let i=0; i<statuses.length; i++){
    if(statuses[i].innerHTML == "Not Yet Available"){
        statuses[i].classList.add("none")
    }
    else if(statuses[i].innerHTML == "completed"){
        statuses[i].classList.add("completed")
    }
    else if(statuses[i].innerHTML == "available but not yet started"){
        statuses[i].classList.add("notStarted")
    }
    else {
        statuses[i].classList.add("otherstatus")
    }
}

let active_inactive = document.getElementsByClassName("False");
for(let i=0; i<active_inactive.length; i++){
    active_inactive[i].classList.add("none")  
}