transcript_uploader = (function () {

	//PUBLIC
	var prepareForm;

	//private
	var readFile, validateFile, showValidationReport, handleError, showErrorBox,
	indexFile, showProgress;

		prepareForm = function () {
			//TU.show_login_status();
			utils.setupAjax();
			if (document.getElementById('transcription_upload_form')) {
				document.getElementById('index_button').disabled = true;
				document.getElementById('transcription_upload_form').reset();
				document.getElementById('transcription_validate_form').reset();
				$('#index_file').off('change.load_index_file');
				$('#index_file').on('change.load_index_file', function () {
					readFile('index_file', 'src', function () {
						document.getElementById('index_button').disabled = false;
						$('#index_button').off('click.index');
						$('#index_button').on('click.index', function () {
							indexFile();
						});
					});
				});
			}
			document.getElementById('validate_button').disabled = true;
			$('#validation_file').off('change.load_validation_file');
			$('#validation_file').on('change.load_validation_file', function () {
				readFile('validation_file', 'validate_src', function() {
					document.getElementById('validate_button').disabled = false;
					$('#validate_button').off('click.validate');
					$('#validate_button').on('click.validate', function () {
						var f, options;
						f = document.getElementById('validation_file').files[0];
						options = forms.serialiseForm('transcription_validate_form');
						validateFile(options.validate_src, escape(f.name));
					});
				});
			});
		};

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
			$('#error_close').off('click.error-close');
			$('#error_close').on('click.error-close', function(event){
                document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
            });
		};

		showMessageBox = function (report) {
			var error_div;
			if (document.getElementById('error') !== null) {
				document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
			}
			error_div = document.createElement('div');
			error_div.setAttribute('id', 'error');
			error_div.setAttribute('class', 'message');
			error_div.innerHTML = '<span id="message_title"><b>Message</b></span><div id="error_close">close</div><br/><br/>' + report;
			document.getElementsByTagName('body')[0].appendChild(error_div);
			$('#error_close').off('click.error-close');
            $('#error_close').on('click.error-close', function(event){
                document.getElementsByTagName('body')[0].removeChild(document.getElementById('error'));
            });
		};

		handleError = function (action, error_report, model) {
			var report;
			console.log(error_report)
			report = 'An error has occurred.<br/>';
			if (error_report.status === 401) {
				report += '<br/>You are not authorised to upload transcriptions into the database.<br/>Please contact the server administrator.';
			} else if (error_report.status === 403) {
				report += '<br/>You are not authorised to upload transcriptions into the database.<br/>Please contact the server administrator.';
			} else if (error_report.status === 415) {
				report += '<br/>It is has not been possible to process your request because '
					+ error_report.responseText + '.';
			} else {
				report += '<br/>The server has encountered an error. Please try again. <br/>If the problem persists please contact the server administrator.';
			}
			showErrorBox(report);
		};

		// show_login_status: function () {
		// 	var elem, login_status_message;
		// 	elem = document.getElementById('login_status');
		// 	if (elem !== null) {
		// 		MAG.AUTH.get_user_info({'success': function(response) {
		// 			if (response.hasOwnProperty('ITSEE_id')) {
		// 				login_status_message = 'logged in as ' + response.ITSEE_id;
		// 			} else {
		// 				login_status_message = 'logged in ';
		// 			}
		// 			elem.innerHTML = login_status_message + '<br/><a href="javascript:MAG.AUTH.log_user_out(\'' + window.location.href + '\')">logout</a>';
		// 		}, 'error': function(response){
		// 			elem.innerHTML = '<br/><a href="javascript:MAG.AUTH.log_user_in(\'' + window.location.href + '\')">login</a>';
		// 		}});
		// 	}
		// },

		showValidationReport = function (report) {
			if (report.valid === true) {
				showMessageBox(report.filename + ' is valid')
			} else {
				showErrorBox(report.filename + ' is not valid for the following reasons:<br/><br/>' + report.errors.join('<br/><br/>') )
			}
		};

		validateFile = function (string, file_name) {
			var options, url, callback;
			// Make URL
			url = '/transcriptions/validate/';
			options = {'src': string, 'file_name': file_name};
			callback = function (resp) {showValidationReport(resp);};
			$.post(url, options, function (response) {callback(response)}, "json").fail(function (response) {
				prepareForm();
				handleError('validate', response);
			});
		};

		indexFile = function () {
			var data, indexing_url, callback, transcription_id;
			data = forms.serialiseForm('transcription_upload_form');
			console.log(data)
			indexing_url = '/transcriptions/index/';
			callback = function (resp) {showProgress(resp);};
			$.post(indexing_url, data, function(response) {callback(response)}, "text").fail(function (response) {
				prepareForm();
				handleError('upload', response);
			});
		};

		showProgress = function (resp) {
			var interval_id, criteria;
			document.getElementById('container').innerHTML = 'indexing ' + resp.split('_')[2];
			criteria = {'identifier': resp};
			interval_id = setInterval(function () {
				document.getElementById('container').innerHTML += '.';
				utils.getItemsFromDatabase('transcriptions', 'privatetranscription', criteria, 'GET', function (response) {
					console.log(response)
					if (response.results[0].loading_complete === true) {
						clearInterval(interval_id);
						showSuccessful(resp.split('_')[2]);
					}
				});
			}, 1000);
		};

		showSuccessful = function (ms) {
			document.getElementById('container').innerHTML =
				'<p>Indexing of ' + ms + ' successful.</p><br/>'
				+ '<input type="button" value="Upload another file" id="upload_another_button"/>'
				+ '<input type="button" value="Return to admin page" id="admin_return_button"/>';
			$('#upload_another_button').off('click.another');
			$('#upload_another_button').on('click.another', function () {reload_page();});
			// $('#admin_return_button').off('click.admin');
			// $('#admin_return_button').on('click.admin', function () {go_to_admin();});
		};

		reload_page = function () {
			location.reload();
		};

		// go_to_admin = function () {
		// 	location.href = 'transcriptions/';
		// };

		readFile = function (file_input_id, store_location_id, onload_callback) {
			var store_elem, input_file, reader;
			store_elem = document.getElementById(store_location_id);
			input_file = document.getElementById(file_input_id).files[0];
			reader = new FileReader();
			reader.onloadend = function () {
				store_elem.value = reader.result;
				if (onload_callback) {
					onload_callback();
				}
			}
			if (input_file) {
				reader.readAsDataURL(input_file);
			} else {
				store_elem.value = '';
			}
		};

		return {
			prepareForm: prepareForm
    };

} () );
