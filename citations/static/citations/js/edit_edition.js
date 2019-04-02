edit_edition = (function () {

	var addEventHandlers, updateIdentifier, loadData, prepareForm;
	//----------------BEGIN PRIVATE METHODS----------------

	addEventHandlers = function () {
		edit.addEventHandlers('edition');
		$('#author').on('change', function (event) {
			edit.filterData('edition', event.target.id, event.target.value, true);
		});
		$('#delete_legacy_edition').on('click', function () {
			var conf;
			conf = confirm('Are you sure you want to delete the legacy data?\nThis should only be done if the data has been encorporated into the edition details.');
			if (conf === true) {
				document.getElementById('legacy_edition_hidden').value = '';
				document.getElementById('legacy_edition_div').style.display = 'none';
			} else {
				return;
			}
		});
	};

	//TODO: not sure we need identifiers once everything settles down (they are important for links now while we are loading data)
	//if we keep them for safety we certainly do not need them to be url safe anymore
//	updateIdentifier = function () {
//
//	};

	//----------------END PRIVATE METHODS----------------

	//----------------BEGIN PUBLIC METHODS----------------

	loadData = function (model, data) {
		var work, series, onlinecorpus;
		work = data.work;
		series = data.series || 'none';
		onlinecorpus = data.onlinecorpus || 'none';

		//dynamically created select fields need to be disabled in callback if they need disabling
		//as the data is not ready in time for them to be disabled in the loadData function
		api.getItemFromDatabasePromise('citations', 'work', work).then(function (work_json){
			var author;
			author = work_json.author || 'none';
			edit.populateAuthor(model, {'select': author}, function () {
				forms.disableFields(['author'], model + '_form');
			});
			edit.populateWork(model, {'select': work, 'author': author}, function () {
				forms.disableFields(['work'], model + '_form');
			});
		});
		
		edit.populateOnlinecorpus(model, {'select': onlinecorpus});
		edit.populateSeries({'selected': series});
		if (data.hasOwnProperty('legacy_edition') && data.legacy_edition !== '') {
			document.getElementById('legacy_edition_div').style.display = 'block';
		}
		edit.loadData(model, data, ['legacy_edition'])
		addEventHandlers();
	};

	prepareForm = function (model, data) {
		edit.populateAuthor(model);
		edit.populateWork(model);
		edit.populateOnlinecorpus(model);
		edit.populateSeries();
		edit.prepareForm(model, data);
		addEventHandlers();
	};

	//----------------END PUBLIC METHODS----------------

	return {
			loadData: loadData,
			prepareForm: prepareForm
			};


} () );
