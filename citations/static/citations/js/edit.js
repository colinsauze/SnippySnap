var testing;
edit = (function () {

	//private
	var getUserStatus, configureForm, configureSubmit, setPreselects,
	addSubmitHandlers, addValidationHandlers;

	//public
	var editData, addEventHandlers, loadData, prepareForm, populateAuthor;

	//called on document ready
	$(function () {
    cits.setUser();
		cits.setProject();
		edit.editData();
  });

	getUserStatus = function () {
		//edition transcribers settings trump online transcribers although ideally one person
		//would only be one at a time in the project so they always get the correct form
		if (cits.project.hasOwnProperty('edition_transcribers')
				&& cits.project.edition_transcribers.indexOf(cits.user.id) !== -1) {
			return 'edition_transcribers';
		}
		if (cits.project.hasOwnProperty('online_transcribers')
				&& cits.project.online_transcribers.indexOf(cits.user.id) !== -1) {
			return 'online_transcribers';
		}
		return null;
	};

	configureForm = function (model) {
    	var user_status;
    	user_status = getUserStatus();
    	//managers always see all parts of the form so only configure if
    	//user is a citation editor
    	if (!cits.user.hasOwnProperty('group_name')
    			|| cits.user.group_name !== 'citation_managers') {
    		if (user_status) {
        		if (cits.project.hasOwnProperty('form_settings')
        				&& cits.project.form_settings
        				&& cits.project.form_settings.hasOwnProperty(model)
        				&& cits.project.form_settings[model].hasOwnProperty(user_status)) {
        			$('.form_section').each(function (){
        				if (cits.project.form_settings[model][user_status].indexOf(this.id) === -1) {
        					this.style.display = 'none';
        				}
        			});
        		}
        	}
    	}
    	return;
    };

    configureSubmit = function (model) {
    	var user_status;
    	user_status = getUserStatus();
    	if (user_status) {
    		if (cits.project.hasOwnProperty('submit_settings')
    				&& cits.project.submit_settings
    				&& cits.project.submit_settings.hasOwnProperty(model)
    				&& cits.project.submit_settings[model].hasOwnProperty(user_status)) {
    			$('#submit_section input').each(function () {
    				if (cits.project.submit_settings[model][user_status].indexOf(this.id) === -1) {
    					this.style.display = 'none';
    				}
    			});
    		}
    	}
    	if (cits.user.hasOwnProperty('group_name')
    			&& cits.user.group_name === 'citation_managers') {
    		document.getElementById('delete').style.display = 'inline';
    	}
    	return;
    };

    //this only deals with preselects that are available in the raw html
    //for things like dynamically populated select boxes the preselects are
    //dealt with as callbacks to the populate select function.
    //It also disables them
    setPreselects = function (model) {
    	var key, for_disable, subkey, user_status;
    	user_status = getUserStatus();
			console.log('*********')
			console.log(JSON.parse(JSON.stringify(cits.project)))
    	if (cits.project.preselects !== null
    			&& cits.project.preselects.hasOwnProperty(model)  ) {
    		for_disable = [];
    		for (key in cits.project.preselects[model]) {
    			if (cits.project.preselects[model].hasOwnProperty(key)) {
    				if (user_status && key === user_status) {
    					for (subkey in cits.project.preselects[model][user_status]) {
    						if (cits.project.preselects[model][user_status].hasOwnProperty(subkey)) {
    							if (document.getElementById(subkey)) {
    								document.getElementById(subkey).value = cits.project.preselects[model][user_status][subkey];
    		    					if (!cits.user.hasOwnProperty('group_name')
    		    							|| (cits.user.group_name !== 'citation_managers'
    		    								&& cits.user.group_name !== 'private_citation_managers')) {
    		    						for_disable.push(subkey);
    		    					}
    							}
    						}
    					}
    				} else if (document.getElementById(key)) {
    					document.getElementById(key).value = cits.project.preselects[model][key];
    					if (!cits.user.hasOwnProperty('group_name')
    							|| (cits.user.group_name !== 'citation_managers'
    								&& cits.user.group_name !== 'private_citation_managers')) {
    						for_disable.push(key);
    					}
    				}
    			}
    		}
    		forms.disableFields(for_disable, model + '_form');
    	}
    };

	//tested in functional tests
	jumpToPageContainingItem = function (model, item) {
		if (window.location.search !== '') {
			window.location = '/citations/' + model + '/' + window.location.search + '&_show=' + item.id;
		} else {
			window.location = '/citations/' + model + '/?_show=' + item.id;
		}
		return;
	};

	//tested in functional tests
    addSubmitHandlers = function(model) {
    	var url_model;
    	url_model = model;
    	if (model === 'privatecitation') {
    		url_model = 'citation';
    	}
    	$('#submit_continue').on('click', function () {
    		submit.submit(model, model + '_form', false, function (json) {
    			var query_dict;
    			query_dict = utils.getCurrentQuery();
    			query_dict['_show'] = json.id;
    			window.location = '/citations/' + url_model + '/edit/' + json.id + '?' + $.param(query_dict);
    		});
    	});
    	$('#submit_another').on('click', function () {
    		submit.submit(model, model + '_form', false, function () {
    			window.location = '/citations/' + url_model + '/edit/' + window.location.search
    		});
    	});
    	$('#submit_home').on('click', function () {
    		//TODO: maybe you should run a functional test against the real database to test this.
    		submit.submit(model, model + '_form', false, function (item) {
    			jumpToPageContainingItem(url_model, item)
    		});
    	});
    	$('#reset_form').on('click', function () {
    		//clear the browser cache (this will lose data but we are not saving and we are reloading from the database in the next line)
    		document.getElementById(model + '_form').reset();
    		//reload the page
    		window.location.reload(false);
    	});
    	$('#delete').on('click', function () {
    		window.location = '/citations/' + url_model + '/delete/' + document.getElementById('id').value + window.location.search;
    	});
    };

    //tested in functional tests
    addValidationHandlers = function (model) {
    	console.log(model)
    	var i, elems;
    	elems = document.getElementById(model + '_form').elements;
        for (i = 0; i < elems.length; i += 1) {
            if (elems[i].tagName === 'TEXTAREA' || elems[i].tagName === 'SELECT'
                || (elems[i].tagName === 'INPUT' && elems[i].type === 'text')) {
            	$(elems[i]).on('change', function (event) {
            		forms.showValidateElement(event.target);
            	});
            }
        }
    };

    getSelectedOptionValue = function (edit_model, select_model, options) {
    	var selected_value;
    	if (options.hasOwnProperty('select')) {
    		return options.select;
    	}
    	if (cits.project.hasOwnProperty('preselects')
    			&& cits.project.preselects.hasOwnProperty(edit_model)
    			&& cits.project.preselects[edit_model].hasOwnProperty(select_model)) {
    		return cits.project.preselects[edit_model][select_model];
    	}
    	return;
    };

    getDataAndPopulate = function (data_type, criteria, options, callback) {
    	var settings;
    	if (typeof options === 'undefined') {
    		options = {};
    	}
			api.getItemsFromDatabasePromise('citations', data_type, criteria).then(function (data) {
				if (typeof options.result_processing !== 'undefined') {
					options.result_processing(data.results, options);
				}
				//if we only have one and we haven't been asked for anything else then select it
				if (typeof options.selected === 'undefined' && data.results.length === 1) {
					options.selected = data.results[0].id;
				}
				settings = {'value_key': options.value_key || 'id',
						 'text_keys': options.text_keys,
						 'selected': options.selected,
						 'reactivate': options.reactivate,
						 'add_class': {'data_key': 'obsolete', 'data_value': true, 'class_name': 'obsolete'}
							};
				forms.populateSelect(data.results, document.getElementById(data_type), settings);
				if (typeof callback !== 'undefined') {
					callback();
				}
			}).catch(function (response) {
				console.log('Something went wrong trying to populate ' + data_type);
			});

    };

	//----------------BEGIN PUBLIC METHODS----------------

    populateAuthor = function (model, options, callback) {
    	var criteria;
    	if (typeof options === 'undefined') {
    		options = {};
    	}
    	options.selected = getSelectedOptionValue(model, 'author', options);
    	//set criteria for search
    	criteria = {'limit': 1000000,
    			'_sort': 'abbreviation',
    			'language': cits.project.language,
    			'_fields': 'id,abbreviation,full_name,obsolete'};
    	if (options.hasOwnProperty('inc_obsolete') && options.inc_obsolete === false) {
    		criteria.obsolete = '!true';
    	}
    	//add in any project criteria that limit author range
    	if (cits.project.hasOwnProperty('author_ids')) {
    		criteria['id'] = cits.project.author_ids.join(',');
    	}
    	options.text_keys = {1 : 'abbreviation', 2 : 'full_name'};
    	getDataAndPopulate('author', criteria, options, callback);
    };

    populateWork = function (model, options, callback) {
    	var criteria;
    	if (typeof options === 'undefined') {
    		options = {};
    	}
    	options.selected = getSelectedOptionValue(model, 'work', options);
    	//get criteria for search
    	criteria = {'limit': 1000000,
    			'_sort': 'abbreviation',
    			'language': cits.project.language,
    			'_fields': 'id,abbreviation,title,obsolete'};
    	if (options.hasOwnProperty('inc_obsolete') && options.inc_obsolete === false) {
    		criteria.obsolete = '!true';
    	}
    	if (options.hasOwnProperty('author')) {
    		criteria['author__id'] = options.author;
    	} else if (cits.project.hasOwnProperty('author_ids')) {
    		criteria['author__id'] = cits.project.author_ids.join(',');
    	}
    	//if we have missing data we need to make sure users can add it
    	if (criteria.hasOwnProperty('author__id') && typeof options.selected === 'undefined') {
    		options.reactivate = true;
    	}
    	options.text_keys = {1 : 'abbreviation', 2 : 'title'}
    	getDataAndPopulate('work', criteria, options, callback);
    };

    populateEdition = function (model, options, callback) {
    	var criteria;
    	if (typeof options === 'undefined') {
    		options = {};
        }
    	options.selected = getSelectedOptionValue(model, 'edition', options);
    	//get criteria for search
    	criteria = {'limit': 1000000,
    			'_sort': 'editor',
    			'_fields': 'id,identifier,onlinecorpus,series,editor,year,legacy_edition'} //we always need onlinecorpus and series in fields as we mention them as Slugs in serialiser
    	if (options.hasOwnProperty('work')) {
    		criteria['work__id'] = options.work;
    	} else if (cits.project.hasOwnProperty('author_ids')) {
    		criteria['work__author__id'] = cits.project.author_ids.join(',');
    	}
    	//if we have missing data we need to make sure users can add it
    	if (criteria.hasOwnProperty('work__id') && typeof options.selected === 'undefined') {
    		options.reactivate = true;
    	}
    	options.text_keys = {'1': 'editor', '2': 'year', '3': 'series', '4': 'legacy_edition'};
    	getDataAndPopulate('edition', criteria, options, callback);
    };

    //options - select - string - the value to select
    populateOnlinecorpus = function (model, options, callback) {
    	var criteria;
    	if (typeof options === 'undefined') {
    		options = {};
        }
    	options.selected = getSelectedOptionValue(model, 'onlinecorpus', options);
    	criteria = {'limit': 1000000,
    			'_sort':'abbreviation',
    			'_fields': 'id,abbreviation'};
    	options.text_keys = 'abbreviation';
    	options.value_key = 'abbreviation';
    	getDataAndPopulate('onlinecorpus', criteria, options, callback);
    };

    populateSeries = function (options, callback) {
    	var criteria;
    	if (options === undefined) {
    		options = {};
    	}
    	criteria = {'limit': 1000000,
    			'_sort':'abbreviation',
    			'_fields': 'id,abbreviation'};
    	options.text_keys = 'abbreviation';
    	options.value_key = 'abbreviation';
    	getDataAndPopulate('series', criteria, options, callback);
    };

    filterData = function (model, trigger, value, inc_obsolete, callback) {
        var options, reactivate;
        if (typeof inc_obsolete === 'undefined') {
            inc_obsolete = true;
        }
        //for populating work based on author this will sometimes then call this again for the work setting
        if (trigger === 'author' && document.getElementById('work') !== null) {
        	options = {'inc_obsolete': inc_obsolete};
        	if (value !== 'none') {
        		options.author = value;
        	}
            edit.populateWork(model, options, function () {
            	forms.showValidateElement(document.getElementById('work'));
            	if (document.getElementById('edition') !== null){
            		filterData(model, 'work', document.getElementById('work').value, inc_obsolete, callback);
            	} else {
            		if (typeof callback !== 'undefined') {
                        callback();
                    }
            	}
            });
        }
        if (trigger === 'work') {
        	options = {};
        	if (value !== 'none') {
        		options.work = value;
        	}
        	edit.populateEdition(model, options, function () {
        		forms.showValidateElement(document.getElementById('edition'));
        		if (typeof callback !== 'undefined') {
                	callback();
                }
        	});
        }
    };

    //all called functions are tested so this is not
	prepareForm = function (model) {
		setPreselects(model);
		configureForm(model);
    	configureSubmit(model);
	};

	loadData = function (model, data, to_disable) {
		var key, subkey, user_status;
		user_status = getUserStatus();
		//first get any project preselect fields and add them to the to_disable list
		if (typeof to_disable === 'undefined') {
			to_disable = [];
		}
		if (cits.user.group_name !== 'citation_managers') {
			if (cits.project.preselects !== null && cits.project.preselects.hasOwnProperty(model)) {
				for (key in cits.project.preselects[model]) {
					if (cits.project.preselects[model].hasOwnProperty(key)) {
						if (user_status && key === user_status) {
							for (subkey in cits.project.preselects[model][user_status]) {
								to_disable.push(subkey);
							}
						} else {
							to_disable.push(key);
						}
					}
				}
	    	}
		}
		forms.populateSimpleForm(data, document.getElementById(model + '_form'));
    	forms.disableFields(to_disable, model + '_form');
    	configureForm(model);
    	configureSubmit(model);
	};

	addEventHandlers = function (model) {
    	addSubmitHandlers(model);
    	addValidationHandlers(model);
    };

	editData = function () {
		var namespace, model, id, editPermissionGranted;
		utils.setupAjax();
		model = $('#container').data('model');
		id = $('#container').data('item_id');
		editPermissionGranted = $('#container').data('permission_granted');
		namespace = 'edit_'+ model
		if (model === 'privatecitation') {
			namespace = 'edit_citation'
		}
		if (id !== '' && editPermissionGranted === 'True') {
			api.getItemFromDatabasePromise('citations', model, id).then(function(data) {
				utils.getFunctionFromString('loadData', namespace)(model, data);
			});
		} else {
			utils.getFunctionFromString('prepareForm', namespace)(model);
		}
	};

	if (testing === true) {
		return {
			getUserStatus: getUserStatus,
			configureForm: configureForm,
			configureSubmit: configureSubmit,
			setPreselects: setPreselects,
			getSelectedOptionValue: getSelectedOptionValue,
			getDataAndPopulate: getDataAndPopulate,
			editData: editData,
			addEventHandlers: addEventHandlers,
			loadData: loadData,
			prepareForm: prepareForm,
			populateAuthor: populateAuthor,
			populateWork: populateWork,
			populateEdition: populateEdition,
			populateOnlinecorpus: populateOnlinecorpus,
			populateSeries: populateSeries,
			filterData: filterData,
			};
	} else {
		return {
			editData: editData,
			addEventHandlers: addEventHandlers,
			loadData: loadData,
			prepareForm: prepareForm,
			populateAuthor: populateAuthor,
			populateWork: populateWork,
			populateEdition: populateEdition,
			populateSeries: populateSeries,
			populateOnlinecorpus: populateOnlinecorpus,
			filterData: filterData,
			getUserStatus: getUserStatus,
			};
	}

	//----------------END PUBLIC METHODS----------------
} () );
