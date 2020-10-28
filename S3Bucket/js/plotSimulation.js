function plotSimulation(chart) {

    // Receive simulation id
	element = document.getElementById("simNameToPlot");
    element.classList.remove("border-danger");
	var simName = element.value;
    //var simulationID = element.value;
	//var simulationId = getInteger(simulationID);

    // Query database (throught lambda function) for the simulation statistics
    var simUsername = document.getElementById('username').value;
	 
    var simParams = {
        username: simUsername,
        simname: simName
    };
	
	// Validate input parameter
	res = validateParams(simParams);
	if(res === "NOK") return;
		
    var apiUrl = 'https://jfd0wf1qhj.execute-api.us-east-2.amazonaws.com/default/get-statistics';

    $.ajax({
        url: apiUrl,
        type: 'POST',
        contentType: 'text/plain',
        data: JSON.stringify(simParams),
        crossDomain: true,
        processData: false,
        success: function (response) {
			
			
			var fieldNameElement = document.getElementById('cardPopSize');
			fieldNameElement.innerHTML = response["population"]
			var fieldNameElement2 = document.getElementById('cardMortality');
			fieldNameElement2.innerHTML = response["mortality_rate"]
			var fieldNameElement3 = document.getElementById('cardInfectious');
			fieldNameElement3.innerHTML = response["infection_rate"]
			
			
			window.chartColors = {
				red: 'rgb(255, 99, 132)',
				orange: 'rgb(255, 159, 64)',
				yellow: 'rgb(255, 205, 86)',
				green: 'rgb(75, 192, 192)',
				blue: 'rgb(54, 162, 235)',
				black: 'rgb(0, 0, 0)'
			};
			
            var ctx = document.getElementById('simulationChart').getContext('2d');
            var myLineChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [...Array(response["treated"].length).keys()],
                    datasets: [{
                        data: response["incubating"],
                        label: "incubating",
                        borderColor: window.chartColors.orange,
                        fill: false
                      }, {
                        data: response["infected"],
                        label: "Infected",
                        borderColor: window.chartColors.red,
                        fill: false
                      }, {
                        data: response["susceptible"],
                        label: "Susceptible",
                        borderColor: window.chartColors.yellow,
                        fill: false
                      }, {
						data: response["dead"],
                        label: "Dead",
                        borderColor: window.chartColors.black,
                        fill: false  
					  }
					  
                    ]
                  },
                  options: {
                    maintainAspectRatio: false,
                    title: {
                      display: true,
                      text: 'Simulation Progress (Infected, Incubating, Susceptible, Dead)'
                    },
                      scales: {
                        xAxes: [{
                            scaleLabel: {
                                labelString: "Days",
                                display: true
                            }
                        }],
                          yAxes: [{
                            scaleLabel: {
                                labelString: "Number of people",
                                display: true
                            }
                        }]
                    }
                  }
            });
			
			var ctx2 = document.getElementById('simulationChart2').getContext('2d');
            var myLineChart = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: [...Array(response["treated"].length).keys()],
                    datasets: [{
                        data: response["treated"],
                        label: "Treated",
                        borderColor: window.chartColors.blue,
                        fill: false
                      }, {
                        data: response["cured"],
                        label: "Cured",
                        borderColor: window.chartColors.green,
                        fill: false
                      }
                    ]
                  },
                  options: {
                    maintainAspectRatio: false,
                    title: {
                      display: true,
                      text: 'Simulation Progress (Cured, Treated)'
                    },
                      scales: {
                        xAxes: [{
                            scaleLabel: {
                                labelString: "Days",
                                display: true
                            }
                        }],
                          yAxes: [{
                            scaleLabel: {
                                labelString: "Number of people",
                                display: true
                            }
                        }]
                    }
                  }
            });
			
			var ctx_pie = document.getElementById('pieChartDay1').getContext('2d');
            var myPieChart = new Chart(ctx_pie, {
                type: 'pie',
				data: {
					datasets: [{
						data: [
							response["incubating_day1"],
							response["treated_day1"],
							response["susceptible_day1"],
							response["infected_day1"],
							response["cured_day1"],
							response["dead_day1"],
						],
						backgroundColor: [
							window.chartColors.orange,
							window.chartColors.blue,
							window.chartColors.yellow,
							window.chartColors.red,
							window.chartColors.green,
							window.chartColors.black,
						],
						label: 'Dataset 1'
					}],
					labels: [
						'Total incubating',
						'Total treated',
						'Total susceptible',
						'Total infected',
						'Total cured',
						'Total dead'
					]
				},
				options: {
					responsive: true
				}
            });
			
			var ctx_pie2 = document.getElementById('pieChartDayLast').getContext('2d');
            var myPieChart = new Chart(ctx_pie2, {
                type: 'pie',
				data: {
					datasets: [{
						data: [
							response["incubating_daylast"],
							response["treated_daylast"],
							response["susceptible_daylast"],
							response["infected_daylast"],
							response["cured_daylast"],
							response["dead_daylast"],
						],
						backgroundColor: [
							window.chartColors.orange,
							window.chartColors.blue,
							window.chartColors.yellow,
							window.chartColors.red,
							window.chartColors.green,
							window.chartColors.black,
						],
						label: 'Dataset 1'
					}],
					labels: [
						'Total incubating',
						'Total treated',
						'Total susceptible',
						'Total infected',
						'Total cured',
						'Total dead'
					]
				},
				options: {
					responsive: true
				}
            });
        },
        error: function (result) {
			
			errorStatus = result.status;
            if(errorStatus === 402){
                window.alert(result.responseText);
                element = document.getElementById("simNameToPlot");
                element.classList.add("border-danger");
            }else{
                console.log("An error has occurred.");
                console.log(result);
            }
			
            console.log("An error has occurred.");
            console.log(result);
        }
    });
  }
  
function validateParams(arrayParams){
    validationResult = "OK";
	missingFields = "";
	if (arrayParams["simname"] === "") {
        element = document.getElementById("simNameToPlot");
        element.classList.add("border-danger");
        missingFields += "- Simulation Name\n";
        validationResult = "NOK";
    }
	
	if(validationResult === "NOK"){
        errorMessage = "";
        if(!(missingFields === "")){
            errorMessage += "Please fill in the following parameters:\n" + missingFields + "\n";
        }
        window.alert(errorMessage);
    }

    return validationResult;
}

function getInteger(input){
    intVal = parseInt(input);

    if(isNaN(intVal)) intVal = 0;

    return intVal;
}