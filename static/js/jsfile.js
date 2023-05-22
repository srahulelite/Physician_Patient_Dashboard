let statuses = document.getElementsByClassName("status");
for(let i=0; i<statuses.length; i++){
    if(statuses[i].innerHTML == "Not Yet Available"){
        statuses[i].classList.add("none")
    }
    else if(statuses[i].innerHTML.includes("complete")){
        statuses[i].classList.add("complete")
    }
    else if(statuses[i].innerHTML.includes("Available a week ago, not yet started")){
        statuses[i].classList.add("notStarted7daysago")
    }
    else if(statuses[i].innerHTML.includes("Started, Not Completed")){
        statuses[i].classList.add("notCompleted")
    }
    else if(statuses[i].innerHTML.includes("Available, Not Yet Started")){
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

