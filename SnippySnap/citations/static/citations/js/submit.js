var testing;
submit = (function () {

	//private
	var handleError, validateForm, save;
	//public
	var showErrorBox, submit;

	//TODO: change the error messages to reflect DJango 409 will never happen because of an id for example
	handleError = function (action, error_report, model) {
        var i, report, key, innerkey, errors;
        report = 'An error has occurred.<br/>';
        if (error_report.status === 401) {
            report += '<br/>You are not authorised to ' + action + ' an entry in the ' + model + ' table.';
        } else if (error_report.status === 409) {
            report += '<br/>It is not possible to ' + action + ' this ' + model + ' because an entry already exists with the same id.';
				} else if (error_report.status === 412) {
						report += '<br/>It is not possible to ' + action + ' this ' + model + ' because the data has been changed in the database since you begain editing.\nPlease refresh the page and make you changes again. text can be copied into a text file and pasted back into the form if necessary.';
        } else if (error_report.status === 404) {
            report += '<br/>It is not possible to ' + action + ' this ' + model + ' because there is no ' + model + ' with this id.';
            report += '<br/><br/>This form can be used to add a new ' + model + '.';
        } else if (error_report.status === 400) {
        	report += '<br/>There were errors in the data. The details are:<br/><br/>';
        	errors = JSON.parse(error_report.responseText)
        	for (key in errors) {
        		if (errors.hasOwnProperty(key)) {
        			if (typeof errors[key][0] === 'string') {
        				report += key + ': ' + errors[key][0] + '<br/>';
        			} else {
    					for (innerkey in errors[key][0]) {
        					report += key + ', ' + innerkey + ': ' + errors[key][0][innerkey] + '<br/>';
        				}
        			}
        		}
        	}
        } else if (error_report.responseText.split('\n').length > 1) {
        	report += '<br/>The error text reads: "' + error_report.responseText.split('\n')[1] + '".<br/>Please try again. <br/>If the problem persists please contact the server administrator.';
        } else {
						report += '<br/>The error text reads: "' + error_report.responseText + '".<br/>'
            report += '<br/>The server has encountered an error. Please try again. <br/>If the problem persists please contact the server administrator.';
        }
        showErrorBox(report);
    };

    //already tested in forms
    //this is here in case we need to add custom validation for things such as either/or requirements
    //like we had in the comcitation data entry form
	validateForm = function (form_id) {
		return forms.validateForm(form_id) ;
	};

	save = function (model, form_id, reload_if_created, success_callback) {
    	var json, url;
    	if (form_id === 'citation_form' || form_id === 'privatecitation_form') {
    		json = edit_citation.customSerialiseForm(form_id);
    	} else {
    		json = forms.serialiseForm(form_id);
    	}
			console.log(json)
			if (json.hasOwnProperty('id') && json.id !== null) {
				api.updateItemInDatabasePromise('citations', model, json).then(function (response){
						console.log('all done')
						success_callback(response);
					}).catch(function (response) {
						console.log('error')
        		handleError('save', response, model);
        	});
    	} else {
				api.createItemInDatabasePromise('citations', model, json).then(function (response){
						success_callback(response, true);
					}).catch(function (response) {
        		handleError('save', response, model);
        	});
    	}
    	return;

    };



	//----------------BEGIN PUBLIC METHODS----------------

    showErrorBox = function (report) {
        var error_div;
        if (document.getElementById('error') !== null) {
            document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
        }
        error_div = document.createElement('div');
        error_div.setAttribute('id', 'error');
        error_div.setAttribute('class', 'error_message');
        error_div.innerHTML = '<span id="error_title"><b>Error</b></span><div id="error_close">close</div><br/><br/>' + report;
        document.getElementsByTagName('body')[0].appendChild(error_div);
        $('#error_close').on('click', function () {
        	document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
        });
    };

	submit = function (model, form_id, reload_if_created, success_callback) {
		var validation;
		console.log('submitting')
		validation = validateForm(form_id);
		console.log(validation)
		if (validation.result === true) {
			save(model, form_id, reload_if_created, success_callback)
			return;
		}
		forms.showValidation(validation);
        showErrorBox('<br/>The data is not valid and cannot be saved. Please fix the errors and resave.'
                + '<br/><br/>Red label text indicates that required data has not been supplied.'
                + '<br/>A red background indicates that the data in that box is not in a format that is valid.');
        return;
	};

	//----------------END PUBLIC METHODS----------------
	if (testing) {
		return {
			submit: submit,
			showErrorBox: showErrorBox,
			save: save,
			validateForm: validateForm,
			handleError: handleError,
			};
	} else {
		return {
			submit: submit,
			showErrorBox: showErrorBox,
			testPromises: function () {

			}


			};
	}


} () );
