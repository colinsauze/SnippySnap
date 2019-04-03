var testing;
forms = (function () {
	var getValue, hasData;

	//NB not all form fields covered - input[radio] for example
	getValue = function (elem) {
		var value;
		value = null;
		if ((elem.tagName === 'INPUT' && (elem.type !== 'checkbox' && elem.type !== 'radio')) || elem.tagName === 'TEXTAREA') {
			value = elem.value;
			if ($(elem).hasClass('stringify')) {
				value = JSON.parse(value);
			} else if ($(elem).hasClass('stringlist')) {
				value = value.split('|');
			} else if ($(elem).hasClass('integer')) {
				value = parseInt(value, 10);
				if (isNaN(value)) {
					value = null;
				}
			} else if ($(elem).hasClass('datetime')) {
				//use null instead of empty string, otherwise just use string as Postgres copes with this
				if (value === '') {
					value = null;
				}
			} else if ($(elem).hasClass('boolean')) {
				//TODO: use value.toLowerCase() but for some reason
				//despite value being a string it gives typeerrors at the mo.
				if (value === 'true') {
					value = true;
				} else if (value === 'false') {
					value = false;
				} else {
					value = null;
				}
			}
		} else if (elem.type === 'checkbox') {
			if ($(elem).hasClass('boolean')) {
				if (elem.checked) {
					value = true;
				} else {
					value = null;
				}
			} else {
				if (elem.checked) {
					value = elem.value;
				}
			}
		} else if (elem.tagName === 'SELECT') {
			value = elem.value;
			if (value !== 'none') {
				if ($(elem).hasClass('integer')) {
					value = parseInt(value, 10);
					if (isNaN(value)) {
						value = null;
					}
				} else {
					if ($(elem).hasClass('boolean')) {
						if (value === 'true') {
							value = true;
						} else {
							if (value === 'false') {
								value = false;
							}
						}
					}
				}
			} else {
				value = null;
			}
		} else {
			if (elem.type === 'radio') {
				if (elem.checked === true) {
					value = elem.value;
				}
			}
		}
		return value;
	};

	/** populates the provided field with the provided data */
    populateField = function (field, data) {
        var i;
        if ((field.tagName === 'INPUT' && field.type !== 'checkbox') ||
                	field.tagName === 'TEXTAREA') {
            if ($.isArray(data)) {
                field.value = data.join('|');
            } else if (Object.prototype.toString.call(data) === '[object Object]') {
            	field.value = JSON.stringify(data);
            } else {
                field.value = data;
            }
        } else if (field.type === 'checkbox') {
            field.checked = data;
        } else if (field.tagName === 'SELECT') {
            if (Object.prototype.toString.call(data) === '[object Number]') {
                data = data.toString();
            }
            if (field.options.length > 0) {
                for (i = 0; i < field.options.length; i += 1) {
                    if (field.options[i].value === data) {
                        field.options[i].selected = true;
                    }
                }
            }
        }
        return;
    };

    getFormElements = function (form_id, elem_list) {
    	var elems, filtered_elems, i;
    	elems = typeof elem_list !== 'undefined' ? elem_list : document.getElementById(form_id).elements;
    	filtered_elems = [];
    	for (i=0; i < elems.length; i+=1) {
    		if (elems[i].disabled === false && (elems[i].name || $(elems[i]).hasClass('data_group'))) {
    			filtered_elems.push(elems[i]);
    		}
    	}
    	return filtered_elems;
    };

    hasData = function (json) {
    	var key;
    	for (key in json) {
    		if (json.hasOwnProperty(key)) {
    			if (json[key] !== null && json[key] !== '') {
    				return true;
    			}
    		}
    	}
    	return false;
    };

	//----------------BEGIN PUBLIC METHODS----------------

    /**TODO: make sure you catch errors with parseInt and leave
    the string as it is - forms should be validating entry
    anyway before this point! */
	serialiseForm = function(form_id, elem_list, prefix) {
    	var i, j, k, elems, json, elem, subelems, key, subjson, value;
		elems = getFormElements(form_id, elem_list);
		json = {};
		for (i = 0; i < elems.length; i += 1) {
			elem = elems[i];
			if ($(elem).hasClass('data_group')) {
				//construct a list of all elements descending from elem
				subelems = [];
				//j records where we are in the list of elements so we can set i
				//to this to continue our loop where we left of with sub elements
				j = i + 1;
				while ($.contains(elem, elems[j])) {
					subelems.push(elems[j]);
					j += 1;
				}
				key = typeof prefix === 'undefined' ? elem.id : elem.id.replace(prefix, '');
				subjson = serialiseForm(form_id, subelems, elem.id + '_');
				if (!$.isEmptyObject(subjson)) {
					if ($(elem).hasClass('objectlist')) {
						console.log(subjson)
						if (hasData(subjson)) {
							try {
								json[key.substring(0, key.lastIndexOf('_'))].push(subjson);
							} catch (err) {
								json[key.substring(0, key.lastIndexOf('_'))] = [ subjson ];
							}
						} else {
							if (!json.hasOwnProperty(key.substring(0, key.lastIndexOf('_')))) {
								json[key.substring(0, key.lastIndexOf('_'))] = [];
							}
						}
					} else if ($(elem).hasClass('stringlist')) {
						//make an array of strings
						json[key] = [];
						for (k in subjson) {
							if (subjson.hasOwnProperty(k)) {
								// don't allow empty strings or null in the array
								if (subjson[k] !== '' && subjson[k] !== null) {
									json[key].push(subjson[k]);
								}
							}
						}
						if (json[key].length === 0) {
							if (!$(elem).hasClass('emptylist')) {
								json[key] = null;
							}
						}
					} else {
						json[key] = subjson;
					}
				} else {
					json[key] = null;
				}
				//reset i to the first element not in our sublist j-1 since we increment j *after* each addition
				i = j - 1;
			} else {
				//TODO: there are different solutions to this in collation_forms in CE_core. Ideally they would be the same! Look at both and pick the best
				value = getValue(elem);
				if (typeof prefix === 'undefined') {
					if (elem.type !== 'radio' || elem.type === 'radio' && value !== null || elem.type === 'radio' && !json.hasOwnProperty(elem.name)) {
						json[elem.name] = value;
					}
				} else {
					if (elem.type !== 'radio' || elem.type === 'radio' && value !== null || elem.type === 'radio' && !json.hasOwnProperty(elem.name.replace(prefix, ''))) {
						json[elem.name.replace(prefix, '')] = value;
					}
				}
			}
		}
		return json;
	};



	/** Populate a simple form from a JSON object
	    A simple form is defined as one which has all
	    fields visible at all times
	    perhaps better called static?
	    requires id on elements to be the same as the
	    corresponding JSON key
	    Embedded objects should have all keys in their
	    ancestor tree joined with '_'
	    inputs:
	    data: the JSON object
	    form: the form object to populate
	    prefix: used internally for dealing with embedded data*/
	populateSimpleForm = function (data, form, prefix) {
	    var field, key, i;
	    if (prefix === undefined) {
	        prefix = '';
	    }
	    for (key in data) {
	        if (data.hasOwnProperty(key)) {
	            if (Object.prototype.toString.call(data[key]) === '[object Object]') {
	            	//then we might have a subobject or we might just need to stringify and store we can only tell from the class on the form item
	            	field = document.getElementById(prefix + key);
	            	if (field && $(field).hasClass('stringify')) {
	            	    populateField(field, data[key]);
	            	} else {
	            		populateSimpleForm(data[key], form, prefix + key + '_');
	            	}
	            } else if ($.isArray(data[key]) && Object.prototype.toString.call(data[key][0]) === '[object Object]') {
	            	populateSimpleForm(data[key], form, prefix + key + '_');
	            } else if ($.isArray(data[key]) && //check if this is a multi field list rather than one that needs to be joined into a single pipe separated value
	            		document.getElementById(prefix + key + '_0')) {
	            	for (i = 0; i < data[key].length; i += 1) {
	            		field = document.getElementById(prefix + key + '_' + i);
	            		if (field) {
	                        populateField(field, data[key][i]);
	                    }
	            	}
	            } else {
	                field = document.getElementById(prefix + key);
	                if (field) {
	                    populateField(field, data[key]);
	                }
	            }
	        }
	    }
	};



    /** Populate a select
     * data = list of json objects containing all data or a list of strings which will be used as value and display
     * select = HTML element to be populated
     * value_key = a single key as a string to use as value attribute for option
     * text_keys = a string, list of strings or object with numbered keys, to use as text of option,
     *              falls through list until it finds one in the data or comma separates numbered fields if object
     * selected = optional argument to say which of the options should be selected
     * add_select = a boolean as to whether to add 'select' with value 'none' to the head of the data list (default true)
     * reactivate = a boolean saying whether this select be reactivated once it is populated*/
	populateSelect = function (data, select, options) {
		var options_html, value_key, text_keys, i, j, template, mapping, text_key, inner_template, inner_template_list, option_text, inner_mapping, option_text_list;
		if (typeof options === 'undefined') {
			options = {};
		}
		options_html = '';
		//this is added by default, add_select must be false to exclude it
		if (!options.hasOwnProperty('add_select') || options.add_select === true) {
			options_html += '<option value="none">select</option>';
		}

		value_key = options.hasOwnProperty('value_key') ? options.value_key : undefined;
		text_keys = options.hasOwnProperty('text_keys') ? options.text_keys : undefined;
		for (i = 0; i < data.length; i += 1) {
			//sort out fall through to a key which does exist if text_keys is an array
			if ($.isArray(text_keys)) {
				for (j = 0; j < text_keys.length; j += 1) {
					if (data[i].hasOwnProperty(text_keys[j])) {
						text_key = text_keys[j];
						break;
					}
				}
			} else {
				text_key = text_keys;
			}
			//if text_key is an object map multiple keys to display in option
			if ($.isPlainObject(text_key)) {
				option_text_list = [];
				j = 1;
				while (text_key.hasOwnProperty(j)) {
					if (data[i].hasOwnProperty(text_key[j]) && data[i][text_key[j]] !== '' && data[i][text_key[j]] !== null) {
						option_text_list.push(data[i][text_key[j]]);
					}
					j += 1;
				}
				option_text = option_text_list.join(', ');
			}
			//final mapping object for option
			mapping = {	val: data[i][value_key] || data[i],
						text: option_text || data[i][text_key] || data[i] || ' ',
						select: "",
						className: ""};
			if (options.hasOwnProperty('selected')
				&& (data[i][value_key] === options.selected
						|| data[i] === options.selected
						|| data[i] === String(options.selected))) {
				mapping.select = ' selected="selected"';
			}
			if (options.hasOwnProperty('add_class')
					&& options.add_class.hasOwnProperty('data_key')
					&& options.add_class.hasOwnProperty('data_value')
					&& options.add_class.hasOwnProperty('class_name')
					&& data[i].hasOwnProperty(options.add_class.data_key)
					&& data[i][options.add_class.data_key] === options.add_class.data_value){
				mapping.className = ' class="' + options.add_class.class_name + '"';
			}
			options_html += '<option value="' + mapping.val + '"' + mapping.className + mapping.select + '>' + mapping.text + '</option>';
		}
		select.innerHTML = options_html;
		if (options.hasOwnProperty('reactivate') && options.reactivate === true) {
			select.disabled = false;
		}
	};


	disableFields = function (field_ids, form_id) {
		var field_name, input_hidden, hidden_value, i;
		for (i = 0; i < field_ids.length; i += 1) {
			if (document.getElementById(field_ids[i])
					&& document.getElementById(field_ids[i]).value !== ''
						&& document.getElementById(field_ids[i]).value !== 'none') {
				input_hidden = document.createElement('input');
				input_hidden.setAttribute('type', 'hidden');
				field_name = document.getElementById(field_ids[i]).getAttribute('name');
				if (field_name) {
					input_hidden.setAttribute('name', field_name);
				}
				input_hidden.setAttribute('id', field_ids[i] + '_hidden');
				hidden_value = getValue(document.getElementById(field_ids[i]));
				if (hidden_value) {
					input_hidden.setAttribute('value', hidden_value);
				} else {
					input_hidden.setAttribute('value', '');
				}
				$(input_hidden).addClass( $('#' + field_ids[i]).attr('class') );
				document.getElementById(form_id).appendChild(input_hidden);
				document.getElementById(field_ids[i]).disabled = 'disabled';
			}
		}
	};

    /**
	 * validate a form to check all fields with required className are complete
	 * and all data entered conforms to type required by className attribute on
	 * element
	 */
	validateForm = function (form_id) {
	    var i, elems, missing_list, invalid_list, result;
	    missing_list = [];
	    invalid_list = [];
	    elems = document.getElementById(form_id).elements;
	    for (i = 0; i < elems.length; i += 1) {
	        result = validateElement(elems[i]);
	        if (result.invalid === true) {
	            invalid_list.push(elems[i].id);
	        }
	        if (result.missing === true) {
	            missing_list.push(elems[i].id);
	        }
	    }
	    if (missing_list.length === 0 && invalid_list.length === 0) {
	        return {'result': true, 'missing': missing_list, 'invalid': invalid_list};
	    }
	    return {'result': false, 'missing': missing_list, 'invalid': invalid_list};
	};

	/** */
    validateElement = function (elem) {
        var missing, invalid;
        missing = false;
        invalid = false;
        //only need to type validate free text fields input
        //type=text and textarea and only
        //if we don't require strings
        if ((elem.tagName === 'INPUT' && elem.type === 'text')
        		|| elem.tagName === 'TEXTAREA') {
            if ($(elem).hasClass('integer') &&
                elem.value.length > 0) {
                if (isNaN(parseInt(elem.value, 10))) {
                    invalid = true;
                }
            }
        }
        //check required fields are not empty or none
        if ($(elem).hasClass('required')
        		&& (elem.value === '' || elem.value === 'none')) {
            missing = true;
        }
        return {'missing': missing, 'invalid': invalid};
    };

	showValidateElement = function (elem) {
		var dict;
        dict = validateElement(elem);
        if (dict.missing === true) {
            $(elem.parentNode).addClass('missing');
        } else {
        	$(elem.parentNode).removeClass('missing');
        }
        if (dict.invalid === true) {
        	$(elem).addClass('error');
        } else {
        	$(elem).removeClass('error');
        }
	};

	showValidation = function(validation_data) {
        var i;
        if (validation_data.result === false) {
            for (i = 0; i < validation_data.missing.length; i += 1) {
                $('#' + validation_data.missing[i]).parent().addClass('missing');
            }
            for (i = 0; i < validation_data.invalid.length; i += 1) {
            	$('#' + validation_data.invalid[i]).addClass('error');
            }
        }
        return;
    };

    if (testing) {
    	return {
    		getValue: getValue,
    		populateField: populateField,
    		getFormElements: getFormElements,
    		populateSimpleForm: populateSimpleForm,
    		populateSelect: populateSelect,
    		disableFields: disableFields,
    		validateForm: validateForm,
    		validateElement: validateElement,
    		showValidation: showValidation,
    		showValidateElement: showValidateElement,
    		serialiseForm: serialiseForm
    		};
    } else {
    	return {
    		populateSimpleForm: populateSimpleForm,
    		populateSelect: populateSelect,
    		disableFields: disableFields,
    		validateForm: validateForm,
    		validateElement: validateElement,
    		showValidation: showValidation,
    		showValidateElement: showValidateElement,
    		serialiseForm: serialiseForm
    		};
    }
//	/** Populate a HTML form from a JSON object
//  complex is defined as a form which alows users to
//  manipulate the fields on display (adding extra rows etc.)
//  this function will attempt to use the add functions to
//  add the fields required to represent the JSON
//  NB if adding fields fails data will be lost so this must be
//  tested well for each form it is used for
//  and the form structure and javascript function names
//  manipulated as necessary to achieve the desired behaviour
//  requires id on elements to be the same as the corresponding
//  JSON key
//  Embedded objects should have all keys in their ancestor tree
//  joined with '_'
//  the function for adding new fields should be 'add' plus the
//  name of the fieldset being added in camelCase minus the number count
//  inputs:
//  data: the JSON object
//  form: the form object to populate
//  js_namespace: the namespace string in which the
//  functions for
//  adding extra fields live (all must be in the same one)
//  prefix_list: used internally for dealing with embedded
//  data*/
//	populateComplexForm = function (data, form, js_name_space, prefix_list) {
//		//assumes ids are the same as json key
//		var field, key, i, fnstring;
//		if (prefix_list === undefined) {
//			prefix_list = [];
//		}
//		for (key in data) {
//			if (data.hasOwnProperty(key)) {
//				if (Object.prototype.toString.call(data[key]) === '[object Object]') {
//					//then we might have a sub-object or we might just need to stringify and store we can only tell from the class on the form item
//					if (prefix_list.length > 0) {
//						field = document.getElementById(prefix_list.join('_') + '_' + key);
//					} else {
//						field = document.getElementById(key);
//					}
//					if (field && $(field).hasClass('stringify')) {
//						populateField(field, data[key]);
//					} else {
//						prefix_list.push(key);
//						populateComplexForm(data[key], form, js_name_space, prefix_list);
//					}
//				//objectlist
//				} else if ($.isArray(data[key]) && Object.prototype.toString.call(data[key][0]) === '[object Object]') {
//					prefix_list.push(key);
//					populateComplexForm(data[key], form, js_name_space, prefix_list);
//				} else {
//					if (prefix_list.length > 0) {
//						field = document.getElementById(prefix_list.join('_') +  '_' +  key);
//					} else {
//						field = document.getElementById(key);
//					}
//					if (field) {
//						populateField(field, data[key]);
//					} else {
//						i = 1;
//						while (field === null && i <= prefix_list.length) {
//							fnstring =  'add' + capitaliseFirst(prefix_list.slice(0, i * -1)).join('');
//							try {
//								utils.getFunctionFromString(fnstring, js_name_space)(data);
//								field = document.getElementById(prefix_list.join('_') + '_' + key);
//								populateField(field, data[key]);
//							} catch (err) {
//								//ignore
//							}
//							i += 1;
//						}
//					}
//				}
//			}
//		}
//		if (prefix_list.length > 0) {
//			prefix_list.pop();
//		}
//		return;
//	};

//	capitaliseFirst = function (list) {
//		var i, j, newList, sublist;
//		console.log('LIST provided ' + list)
//		newList = [];
//		for (i = 0; i < list.length; i += 1) {
//			if (list[i].indexOf('_') !== -1) {
//				sublist = list[i].split('_');
//				for (j = 0; j < sublist.length; j += 1) {
//					newList.push(sublist[j].charAt(0).toUpperCase() + sublist[j].slice(1));
//				}
//			}
//			else {
//				newList.push(list[i].charAt(0).toUpperCase() + list[i].slice(1));
//			}
//		}
//		return newList
//	};

	//----------------END PUBLIC METHODS----------------
} () );
