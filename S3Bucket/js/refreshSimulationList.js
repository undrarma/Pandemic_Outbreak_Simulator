function refreshSimulationList(){
	
	// Get username
    var simUsername = document.getElementById('username').value;

	var simParams = {
        username: simUsername
    };
	
	apiUrl = 'https://jfd0wf1qhj.execute-api.us-east-2.amazonaws.com/default/run-simulation';
	
	$.ajax({
        url: apiUrl,
        type: 'POST',
        contentType: 'text/plain',
        data: JSON.stringify(simParams),
        crossDomain: true,
        processData: false,
		beforeSend: function(){
			
			// Show loading icon
			$("#barSimList").fadeOut();
			$("#spinner").show();			
		},
		success: function (response) {
			
			// Clear the list
			$("#simList").html("");
			var item = "<a onclick=\"refreshSimulationList()\" class=\"btn btn-success btn-user btn-block text-white\">Refresh list</a>";
			$(item).appendTo('#simList');

			// Receive the json from the response
			var json = $.parseJSON(response);

			// Append all the available simulations to the corresponding div element
			$.each(json, function(index) {
				var item = "<a class=\"collapse-item\">"+json[index].simulation_name+"</a>"
				$(item).appendTo('#simList');
			});	

			// Hide loading icon
			$("#barSimList").fadeIn();
			$("#spinner").hide();
		},
        error: function (result) {
			// Hide loading icon
			$("#barSimList").fadeIn();
			$("#spinner").hide();
			
            console.log("An error has occurred.");
            console.log(result);
        }
    });
}

