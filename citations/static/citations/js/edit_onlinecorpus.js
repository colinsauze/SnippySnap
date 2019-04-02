edit_onlinecorpus = (function () {
	
	var addEventHandlers, updateIdentifier, loadData, prepareForm;
	
	//----------------BEGIN PRIVATE METHODS----------------
	
	addEventHandlers = function () {
		edit.addEventHandlers('onlinecorpus');
	};
	
	//----------------END PRIVATE METHODS----------------
	
	//----------------BEGIN PUBLIC METHODS----------------
	
	loadData = function (model, data) {
		edit.loadData(model, data)
		addEventHandlers();
	};
	
	prepareForm = function (model, data) {
		edit.prepareForm(model, data);
		addEventHandlers();
		//special handler for new records
//		$('#abbreviation').on('keyup change', function() {
//			updateIdentifier();
//		});
	};
	
	//----------------END PUBLIC METHODS----------------
	
	return {
			loadData: loadData,
			prepareForm: prepareForm
			};
	
	
} () );