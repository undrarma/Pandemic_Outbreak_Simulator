function startSimulation() {
    element = document.getElementById("simName");
    element.classList.remove("border-danger");
    element = document.getElementById("popSize");
    element.classList.remove("border-danger");
	element = document.getElementById("mortality_rate");
    element.classList.remove("border-danger");
	element = document.getElementById("infection_rate");
    element.classList.remove("border-danger");
	element = document.getElementById("numDays");
    element.classList.remove("border-danger");

    simUsername = document.getElementById('username').value;
    simName = $('#simName').val();
    popSize = $('#popSize').val();
    susceptibility = $('#susceptibility').val();
    infectious = $('#infectious').val();
    contagious = $('#contagious').val();
    treatment = $('#treatment').val();
    cure = $('#cure').val();
	mortalityR = $('#mortality_rate').val();
	infectionR = $('#infection_rate').val();
	numDays = $('#numDays').val();

    susRate = getFloat(susceptibility,1);
    infRate = getFloat(infectious,1);
    contRate = getFloat(contagious,1);
    treatRate = getFloat(treatment,1);
    cureRate = getFloat(cure,1);
	mortalityRate = getFloat(mortalityR,1);
	infectionRate = getFloat(infectionR,1);
    numDays = getInteger(numDays);
	
    document.forms["simForm"].elements["susceptibility"].value = susRate;
    document.forms["simForm"].elements["infectious"].value = infRate;
    document.forms["simForm"].elements["contagious"].value = contRate;
    document.forms["simForm"].elements["treatment"].value = treatRate;
    document.forms["simForm"].elements["cure"].value = cureRate;
	document.forms["simForm"].elements["mortality_rate"].value = mortalityRate;
	document.forms["simForm"].elements["infection_rate"].value = infectionRate;
	
    var simParams = {
        username: simUsername,
        simname: simName,
		mortality_rate: mortalityRate,
		infection_rate: infectionRate,
        population: popSize,
        susceptibility: susRate,
        infectious: contRate,
        contagious: infRate,
        treatment: treatRate,
        cure: cureRate,
		days: numDays
    };
	
    res = validateParams2(simParams);
    if(res === "NOK") return;
    else if(res === "OK_EMPTY"){
        simParams["susceptibility"] = 99;
        simParams["infectious"] = 1;
    }
    console.log(JSON.stringify(simParams));
    // return; //Comment this return to test connection with API Gateway

	// Show loading bar until seccess message is received
	//document.getElementById("loader").style = True;

    apiUrl = 'https://jfd0wf1qhj.execute-api.us-east-2.amazonaws.com/default/simulation-main';

    // // Call API Gateway GET Item
    // $.ajax({
    //     url: apiUrl,
    //     type: 'GET',
    //     contentType: 'text/plain',
    //     data: simName,
    //     crossDomain: true,
    //     success: function (result) {
    //         window.alert(result)
    //     },
    //     error: function (result) {
    //         console.log("An error has occurred.");
    //         console.log(result);
    //     }
    // });

    $.ajax({
        url: apiUrl,
        type: 'POST',
        contentType: 'text/plain',
        data: JSON.stringify(simParams),
        crossDomain: true,
        processData: false,
		beforeSend: function(){
			
			// Show loading icon
			$("#main").fadeOut();
			$("#spinner").show();			
			//$("#loader").show();
			
		},
        success: function (result) {
            // Retrieve simulation id from API response
            resArray = result.split(" ");
            id = resArray[resArray.length - 1];
            console.log(id);
            // document.getElementById('simulationID').value = id;

            // Set validation button as green (success)
            element = document.getElementById("validateBtn");
            element.classList.remove("btn-info");
            element.classList.add("btn-success");

            // Set run button as blue (update function to enable run simulation)
            //element = document.getElementById("runBtn");
            //element.classList.remove("btn-secondary");
            //element.classList.add("btn-info");
            //element.setAttribute('onclick','runSimulation(1)')

            // Put parameters in UI
            //document.getElementById('cardSimName').innerHTML = simName;
            //document.getElementById('cardPopSize').innerHTML = popSize;
            //document.getElementById('cardSusceptibility').innerHTML = susRate + "%";
            //document.getElementById('cardInfectious').innerHTML = infRate + "%";
            //document.getElementById('cardContagious').innerHTML = contRate + "%";
            //document.getElementById('cardTreatment').innerHTML = treatRate + "%";
            //document.getElementById('cardCure').innerHTML = cureRate + "%";
			
			// Hide loading icon
			$("#main").fadeIn();
			$("#spinner").hide();
			//$("#loader").hide();
		},
        error: function (result) {
			
			// Hide loading icon
			$("#main").fadeIn();
			$("#spinner").hide();
			$("#loader").hide();
			
            errorStatus = result.status;
            if(errorStatus === 401){
                window.alert(result.responseText);
                element = document.getElementById("simName");
                element.classList.add("border-danger");
            }else{
                console.log("An error has occurred.");
                console.log(result);
            }
        }
    });
}

function validateParams2(arrayParams){
    validationResult = "OK";
    missingFields = "";
    invalidPercentage = "";
    allEmpty = false;
	
	missingFields += arrayParams["days"]+"ssss\n";

    if (arrayParams["simname"] === "") {
        element = document.getElementById("simName");
        element.classList.add("border-danger");
        missingFields += "- Simulation Name\n";
        validationResult = "NOK";
    }
    if (arrayParams["population"] === "") {
        element = document.getElementById("popSize");
        element.classList.add("border-danger");
        missingFields += "- Population Size\n";
        validationResult = "NOK";
    }
	if (arrayParams["mortality_rate"] === "" || arrayParams["mortality_rate"] === 0  || arrayParams["mortality_rate"] > 100) {
        element = document.getElementById("mortality_rate");
        element.classList.add("border-danger");
        missingFields += "- Mortality Rate\n";
        validationResult = "NOK";
    }
	if (arrayParams["infection_rate"] === "" || arrayParams["infection_rate"] === 0  || arrayParams["infection_rate"] > 100) {
        element = document.getElementById("infection_rate");
        element.classList.add("border-danger");
        missingFields += "- Infection Rate\n";
        validationResult = "NOK";
    }
	if(arrayParams["days"] < 1){
        element = document.getElementById("numDays");
        element.classList.add("border-danger");
		missingFields += "- Duration\n";
        validationResult = "NOK";
    }

    p1 = arrayParams["susceptibility"];
    p2 = arrayParams["infectious"];
    p3 = arrayParams["contagious"];
    p4 = arrayParams["treatment"];
    p5 = arrayParams["cure"];

    if(p1 || p2 || p3 || p4 || p5){
        var totalP = 0;
        totalP += parseFloat(p1);
        totalP += parseFloat(p2);
        totalP += parseFloat(p3);
        totalP += parseFloat(p4);
        totalP += parseFloat(p5);
        if(totalP !== 100){
            invalidPercentage = "Please make sure the provided percentages sum 100%";
            validationResult = "NOK";
        }
    }else if(!p1 && !p2 && !p3 && !p4 && !p5){
        allEmpty = true;
    }

    if(validationResult === "NOK"){
        errorMessage = "";
        if(!(missingFields === "")){
            errorMessage += "Please fill in the following parameters:\n" + missingFields + "\n";
        }
        if(!(invalidPercentage === "")){
            errorMessage += invalidPercentage;
        }
        window.alert(errorMessage);
    }else if(allEmpty) validationResult += "_EMPTY";

    return validationResult;
}

function getFloat(input, fractionDig){
    floatVal = parseFloat(input).toFixed(fractionDig);

    if(isNaN(floatVal)) floatVal = 0;

    return floatVal;
}

function getInteger(input){
    intVal = parseInt(input);

    if(isNaN(intVal)) intVal = 0;

    return intVal;
}

function runSimulation(validated){
    //element = document.getElementById("numDays");
    //element.classList.remove("border-danger");

    if(validated === 0){
        return false;
    }

    simID = document.getElementById('simulationID').value;
    //numDays = $('#numDays').val();

    //numDays = getInteger(numDays);

    //if(numDays < 1){
    //    element = document.getElementById("numDays");
    //    element.classList.add("border-danger");
    //    window.alert("Please input a valid number (Positive integer)");
    //    return false;
    //}

    apiUrl = 'https://jfd0wf1qhj.execute-api.us-east-2.amazonaws.com/default/run-simulation';

    var runParams = {
        sim_id: simID,
        days: numDays
    };

    console.log(JSON.stringify(runParams));

    $.ajax({
        url: apiUrl,
        type: 'POST',
        contentType: 'text/plain',
        data: JSON.stringify(runParams),
        crossDomain: true,
        processData: false,
        success: function (result) {
            window.alert(result);
        },
        error: function (result) {
            console.log("An error has occurred.");
            console.log(result);
        }
    });
}