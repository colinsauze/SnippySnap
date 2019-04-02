
cits = (function () {

	var project, user, setProject, setUser, doDelete;


	//----------------BEGIN PUBLIC METHODS----------------

	project = {};
	user = {};

	setProject = function () {
		var projectData = $('#container').data('project');
		this.project = projectData;
		//if there is a 'project' element on the form set it with the id
		if (document.getElementById('project')) {
			document.getElementById('project').value = this.project.id;
		}
	};

	setUser = function () {
		var userData = $('#container').data('user');
		this.user = userData;
	};

//	deleteData = function (data) {
//		console.log(data)
//		if (data.hasOwnProperty('citation') && data.citation.length > 0) {
//
//		}
//	};

	addDeleteEventHandlers = function (model_label) {
		$('.delete_logo').on('click', function (event) {
			doDelete(event.target.id, false);
		});
		$('.delete_dep_logo').on('click', function (event) {
			doDelete(event.target.id, true);
		});
		$('.delete_possible_author_reference_logo').on('click', function (event) {
			deletePossibleAuthorReference(event.target.id);
		});
		$('.delete_edition_reference_logo').on('click', function (event) {
			deleteEditionReference(event.target.id);
		});
		$('.delete_series_reference_logo').on('click', function (event) {
			deleteSeriesReference(event.target.id);
		});
		$('.delete_onlinecorpus_reference_logo').on('click', function (event) {
			deleteOnlinecorpusReference(event.target.id);
		});
		$('#cancel_delete').on('click', function () {
			window.location.href = '/citations/' + model_label + window.location.search;
		});
	};

	deletePossibleAuthorReference = function (details) {
		var temp, model, model_id, field, field_id, success_callback, error_callback;
		temp = details.split('_');
		model = temp[1];
		model_id = temp[2];
		field = temp[3];
		field_id = temp[4];
		api.deleteM2MItemFromDatabasePromise('citations', model, model_id, 'other_possible_authors', field, field_id).then(function (response){
			location.reload()
		}).catch(function (response) {
      submit.showErrorBox('It was not possible to delete the possible author reference in this work.<br/>Please try again. <br/>If the problem persists please contact the server administrator.');
    });
	};

	deleteSeriesReference = function(details) {
  var temp, model, id, success_callback, error_callback;
  temp = details.split('_');
  model = temp[1];
  id = temp[2];
  api.updateFieldsInDatabasePromise('citations', model, id, {
    'series': null
  }).then(function() {
    location.reload()
  }).catch(function(response) {
    submit.showErrorBox('It was not possible to delete the series reference in this edition.<br/>Please try again. <br/>If the problem persists please contact the server administrator.');
  });
};

	deleteEditionReference = function(details) {
	  var temp, model, id, success_callback, error_callback;
	  temp = details.split('_');
	  model = temp[1];
	  id = temp[2];
	  api.updateFieldsInDatabasePromise('citations', model, id, {
	    'edition': null
	  }).then(function() {
	    location.reload()
	  }).catch(function(response) {
	    submit.showErrorBox('It was not possible to delete the edition reference in this citation.<br/>Please try again. <br/>If the problem persists please contact the server administrator.');
	  });
	};

	deleteOnlinecorpusReference = function(details) {
	  var temp, model, id, success_callback, error_callback;
	  temp = details.split('_');
	  model = temp[1];
	  id = temp[2];
	  api.updateFieldsInDatabasePromise('citations', model, id, {
	    'onlinecorpus': null
	  }).then(function() {
	    location.reload()
	  }).catch(function(response) {
	    submit.showErrorBox('It was not possible to delete the onlinecorpus reference in this ' + model + '.<br/>Please try again. <br/>If the problem persists please contact the server administrator.');
	  });
	};

	doDelete = function (details, dependency) {
		var temp, model, model_label, id, success_callback, error_callback;
		temp = details.split('_');
		model = temp[1];
		model_label = model;
		if (model === 'privatecitation') {
		    model_label = 'citation';
		}
		id = temp[2];
		api.deleteItemFromDatabasePromise('citations', model, id).then(function (response) {
			if (response === 204 && dependency === false) {
				//if successfully deleted the main item relocate to the item list
				window.location.href = '/citations/' + model_label + window.location.search;
			} else {
				//if we get anything other than a successful delete show a this item does not exist page via the view (404)
				location.reload();
			}
		}).catch(function (response) {
			if (response.responseText.indexOf('ProtectedError') !== -1) {
				submit.showErrorBox('It was not possible to delete this ' + model_label + ' as there are other database entries that are dependent upon it.<br/>Please delete the dependencies and try again.');
			} else if (response.status === 403) {
				submit.showErrorBox('You do not have the correct permissions to delete this ' + model_label + '.');
			} else {
				submit.showErrorBox('It was not possible to delete this ' + model_label + '.<br/>Please try again. <br/>If the problem persists please contact the server administrator.');
			}
		});

	};

	return {
			setProject: setProject,
			project: project,
			setUser: setUser,
			user: user,
			addDeleteEventHandlers: addDeleteEventHandlers,
			//deleteData: deleteData,
			};
	//----------------END PUBLIC METHODS----------------

} () );
