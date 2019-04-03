/*
*	utils.js
*	get and display data for data lists
*/
var testing;
utils = (function () {
	//public
	var getCurrentQuery, getCookie, getCurrentLocationSearch, pad2;

	//----------------BEGIN PUBLIC METHODS----------------

	pad2 = function (number) {
		if (number < 10) {
			return '0' + number;
		}
		return number;
	};

	//helper function so we can stub it for testing getCurrentQuery
	getCurrentLocationSearch = function () {
		return window.location.search;
	};

	getCurrentQuery = function () {
		var qstring;
		qstring = utils.getCurrentLocationSearch();
		if (qstring === '' || qstring === '?') {
			return {};
		}
		return getObjectFromQueryString(qstring);
	};

	getObjectFromQueryString = function (qstring) {
		var qdict, qlist, i, argpair;
		qdict = {};
		if (qstring === '') {
			return {};
		}
		qlist = qstring.replace('?', '').split('&');
		for (i = 0; i < qlist.length; i += 1) {
			argpair = qlist[i].split('=');
			qdict[argpair[0]] = argpair[1];
		}
		return qdict;
	};

	getCookie = function (name) {
		var cookieValue, cookies, i, cookie;
	    cookieValue = null;
	    if (document.cookie && document.cookie != '') {
	        cookies = document.cookie.split(';');
	        for (i = 0; i < cookies.length; i++) {
	            cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	};

    /** Performs a template substitution, returning a new string.
    mapping is an object with keys that match the placeholders
    in the template. */
	templateSubstitute = function (template, mapping) {
		return template.replace((/\\?\{([A-Za-z0-9_\-]+)\}/g),
				function (match, name) {
					if (match.charAt(0) === '\\') {
						return match.slice(1);
					}
					return (mapping[name] !== null) ? mapping[name] : '';
				}
		);
	};

	//don't think we need this any more - not tested
	getIdSafeString = function (string) {
        string = $.trim(string);
        string = string.replace(/\?/g, '');
        string = string.replace(/\./g, '');
        string = string.replace(/ /g, '-');
        string = string.replace(/=/, '');
        string = string.replace(/#/g, '');
        string = string.replace(/%/g, '');
        string = string.replace(/\*/g, '');
        string = string.replace(/{/g, '');
        string = string.replace(/}/g, '');
        string = string.replace(/\(/g, '');
        string = string.replace(/\)/g, '');
        string = string.replace(/\\/g, '');
        string = string.replace(/:/g, '');
        string = string.replace(/</g, '');
        string = string.replace(/>/g, '');
        string = string.replace(/\//g, '');
        string = string.replace(/\+/g, '');
        string = string.replace(/&/g, '');
        string = string.replace(/,/g, '');
        return string;
    };

    deleteElement = function (elem) {
    	elem.parentNode.removeChild(elem);
    };

	getFunctionFromString = function (fnname, namespace) {
		if (typeof namespace === 'undefined') {
			return window[fnname];
		}
		return window[namespace][fnname];
    };

    //TODO: see if we need to delete the csrfmiddleware token - I'm not sure it is there
    //it might be in the form but it might not be needed
    createItemInDatabase = function (app, model, data, success_callback, error_callback) {
    	delete data['csrfmiddlewaretoken'];
    	$.ajax({'url': '/api/' + app + '/' + model + '/create/',
    			'headers': {'Content-Type': 'application/json'},
    			'dataType': 'json',
    			'method': 'POST',
    			'data': JSON.stringify(data)}
    	).done(function (response) {
    		if (typeof success_callback !== 'undefined') {
    			success_callback(response);
    		}
    	}).fail(function (response) {
    		if (typeof error_callback !== 'undefined') {
    			error_callback(response)
    		}
    	});
    	return;
    };//{'json': JSON.stringify(data), 'csrfmiddlewaretoken': csrf_token}, 'success': function (response) {

		createItemInDatabasePromise = function (app, model, data) {
			delete data['csrfmiddlewaretoken'];
			return new Promise(function (resolve, reject) {
				$.ajax({'url': '/api/' + app + '/' + model + '/create/',
	    			'headers': {'Content-Type': 'application/json'},
	    			'dataType': 'json',
	    			'method': 'POST',
	    			'data': JSON.stringify(data)}
	    	).then(function (response) {
					resolve(response);
				}).catch(function (response) {
					reject(response);
				});
			});
		};

    //TODO: see if we need to delete the csrfmiddleware token - I'm not sure it is there
    //it might be in the form but it might not be needed
    updateItemInDatabase = function (app, model, data, success_callback, error_callback) {
    	console.log(JSON.parse(JSON.stringify(data)))
    	delete data['csrfmiddlewaretoken'];
    	$.ajax({'url': '/api/' + app + '/' + model + '/update/' + data.id,
    			'headers': {'Content-Type': 'application/json'},
    			'dataType': 'json',
    			'method': 'PUT',
    			'data': JSON.stringify(data)}
    	).done(function (response) {//{'json': JSON.stringify(data), 'csrfmiddlewaretoken': csrf_token}, 'success': function (response) {
    		console.log('done and happy')
    		if (typeof success_callback !== 'undefined') {
    			success_callback(response);
    		}
    	}).fail(function (response) {
    		console.log('failed and miserable')
    		if (typeof error_callback !== 'undefined') {
    			error_callback(response);
    		}
    	});
    	return;
    };

		updateItemInDatabasePromise = function (app, model, data) {
			delete data['csrfmiddlewaretoken'];
			return new Promise(function (resolve, reject) {
				$.ajax({'url': '/api/' + app + '/' + model + '/update/' + data.id,
	    			'headers': {'Content-Type': 'application/json'},
	    			'dataType': 'json',
	    			'method': 'PUT',
	    			'data': JSON.stringify(data)}
	    	).then(function (response) {
					resolve(response);
				}).catch(function (response) {
					reject(response);
				});
			});
		};


    updateFieldsInDatabase = function (app, model, id, data, success_callback, error_callback) {
    	$.ajax({'url': '/api/' + app + '/' + model + '/update/' + id,
    			'headers': {'Content-Type': 'application/json'},
    			'dataType': 'json',
    			'method': 'PATCH',
    			'data': JSON.stringify(data)}
    	).done(function (response) {
    		if (typeof success_callback !== 'undefined') {
    			success_callback(response);
    		}
    	}).fail(function (response) {
    		if (typeof error_callback !== 'undefined') {
    			error_callback(response)
    		}
    	});
    	return;
    };

		updateFieldsInDatabasePromise = function (app, model, id, data, etag) {
			return new Promise(function (resolve, reject) {
				$.ajax({'url': '/api/' + app + '/' + model + '/update/' + id,
						'headers': {'Content-Type': 'application/json', 'If-Match': etag},
						'dataType': 'json',
						'method': 'PATCH',
						'data': JSON.stringify(data)}
				).then(function (response, textStatus, jqXHR) {
					console.log('boo')
					console.log(jqXHR.getAllResponseHeaders())
					console.log(jqXHR.getResponseHeader('etag'))
					resolve(response, jqXHR.getResponseHeader('etag'));
				}).catch(function (response) {
					reject(response);
				});
			});
		};

    deleteM2MItemFromDatabase = function (app, model, model_id, fieldname, item_model, item_id, success_callback, error_callback) {
        $.ajax({'url': '/api/' + app + '/' + model + '/' + model_id + '/' + fieldname + '/delete/' + item_model + '/' + item_id,
                'headers': {'Content-Type': 'application/json'}, //'X-CSRFToken': csrf_token,
                'dataType': 'json',
                'method': 'PATCH'
                }
        ).done(function (response) {//{'json': JSON.stringify(data), 'csrfmiddlewaretoken': csrf_token}, 'success': function (response) {
            if (typeof success_callback !== 'undefined') {
                success_callback(response);
            }
        }).fail(function (response) {
            if (typeof error_callback !== 'undefined') {
                error_callback(response)
            }
        });
        return;
    };

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    };

    function setupAjax() {
    	$.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });
    };

    //TODO: at the moment this actually just gets a list based on id and takes the first one (there should only be one because of id)
    //this is so we also filter by project to check project suitability but maybe we want to change this so
    //it is more efficient and just does a get maybe by adding id to the end of the url
    //if we do need filtering you can use get_items and then select the first
    // getItemFromDatabase = function (app, model, id, success_callback, error_callback) {
    // 	$.ajax({'url': '/api/' + app + '/' + model,
	  //   		'method': 'GET',
	  //   		'data': {'id': id}}
	  //   ).done(function (response) {
    // 		if (typeof success_callback !== 'undefined') {
    // 			success_callback(response.results[0]);
    // 		}
    // 	}).fail(function (response) {
    // 		if (typeof error_callback !== 'undefined') {
    // 			error_callback(response);
    // 		}
    // 	});
    // 	return;
    // };
		//
		// getItemFromDatabasePromise = function (app, model, id) {
		// 	return new Promise(function (resolve, reject) {
		// 		$.ajax({'url': '/api/' + app + '/' + model,
		//     		'method': 'GET',
		//     		'data': {'id': id}}
		//     ).then(function(response){
		// 			resolve(response.results[0]);
		// 		}).catch(function (response) {
		// 			reject(response);
		// 		});
		// 	});
		// };

		//Above is the old version of these functions, as far as I can tell the
		//citations app should continue to work but it should be changed anyway to support optimistic locking which currently would not work



		getItemFromDatabase = function (app, model, id, success_callback, error_callback) {
			$.ajax({'url': '/api/' + app + '/' + model + '/' + id,
					'method': 'GET'}
			).done(function (response, textStatus, jqXHR) {
				if (typeof success_callback !== 'undefined') {
					success_callback(response, jqXHR.getResponseHeader('etag'));
				}
			}).fail(function (response) {
				if (typeof error_callback !== 'undefined') {
					error_callback(response);
				}
			});
			return;
		};

		getItemFromDatabasePromise = function (app, model, id) {
			return new Promise(function (resolve, reject) {
				$.ajax({'url': '/api/' + app + '/' + model + '/' + id,
						'method': 'GET'}
				).then(function(response, textStatus, jqXHR) {
					console.log('boo')
					console.log(jqXHR.getAllResponseHeaders())
					resolve(response);
				}).catch(function (response) {
					reject(response);
				});
			});
		};

    getItemsFromDatabase = function (app, model, criteria, method, success_callback, error_callback) {
    	$.ajax({'url': '/api/' + app + '/' + model,
    			'method': method,
    			'data': criteria}
    	).done(function (response) {
    		if (typeof success_callback !== 'undefined') {
    			success_callback(response);
    		}
    	}).fail(function (response) {
    		if (typeof error_callback !== 'undefined') {
    			error_callback(response);
    		}
    	});
    	return;
    };

		getItemsFromDatabasePromise = function (app, model, criteria, method) {
			if (typeof method === undefined) {
				method = 'GET';
			}
			return new Promise(function (resolve, reject) {
				$.ajax({'url': '/api/' + app + '/' + model,
	    			'method': method,
	    			'data': criteria}
	    	).then(function(response) {
					resolve(response);
				}).catch(function (response) {
					reject(response);
				});
			});
    };

    deleteItemFromDatabase = function (app, model, id, success_callback, error_callback) {
    	$.ajax({'url': '/api/' + app + '/' + model + '/delete/' + id,
    			'method': 'DELETE'}
    	).done(function (response, textStatus, jqXHR) {
    		if (typeof success_callback !== 'undefined') {
    			success_callback(response, jqXHR.status);
    		}
    	}).fail(function (response) {
    		if (typeof error_callback !== 'undefined') {
    			error_callback(response);
    		}
    	});
    	return;
    };

		deleteItemFromDatabasePromise = function (app, model, id) {
			return new Promise(function (resolve, reject) {
				$.ajax({'url': '/api/' + app + '/' + model + '/delete/' + id,
	    			'method': 'DELETE'}
	    	).then(function (response, textStatus, jqXHR) {
					resolve(response, jqXHR.status);
				}).catch(function (response) {
					reject(response);
				});
			});
		};

//this was not being used at the point of testing - there is no matching api url
    //TODO: should this be getting the first from the list
    //or should the python side be returning just one?
//    getCurrentUser = function (success_callback) {
//    	$.ajax({'url': '/api/whoami/',
//    			'method': 'GET'}
//    	).done(function (response) {
//    		response = JSON.parse(response)[0];
//    		if (typeof success_callback !== 'undefined') {
//    			success_callback(response);
//    		}
//    	});
//    	return;
//    };

	if (testing) {
		return {getCurrentLocationSearch: getCurrentLocationSearch,
			getCurrentLocationSearch: getCurrentLocationSearch,
			getCurrentQuery : getCurrentQuery,
			getObjectFromQueryString: getObjectFromQueryString,
			getCookie: getCookie,
			getFunctionFromString: getFunctionFromString,
			getIdSafeString: getIdSafeString,
			templateSubstitute: templateSubstitute,
			getItemFromDatabase: getItemFromDatabase,
			getItemsFromDatabase: getItemsFromDatabase,
			createItemInDatabase: createItemInDatabase,
			updateItemInDatabase: updateItemInDatabase,
			//getCurrentUser: getCurrentUser,
			deleteElement: deleteElement,
			setupAjax: setupAjax,
			deleteItemFromDatabase: deleteItemFromDatabase,
			updateFieldsInDatabase: updateFieldsInDatabase,
			deleteM2MItemFromDatabase: deleteM2MItemFromDatabase,
			pad2: pad2
			};
	} else {
		return {getCurrentLocationSearch: getCurrentLocationSearch,
			getCurrentQuery : getCurrentQuery,
			getObjectFromQueryString: getObjectFromQueryString,
			getCookie: getCookie,
			getFunctionFromString: getFunctionFromString,
			getIdSafeString: getIdSafeString,
			templateSubstitute: templateSubstitute,
			getItemFromDatabase: getItemFromDatabase,
			getItemsFromDatabase: getItemsFromDatabase,
			createItemInDatabase: createItemInDatabase,
			updateItemInDatabase: updateItemInDatabase,
			//getCurrentUser: getCurrentUser,
			deleteElement: deleteElement,
			setupAjax: setupAjax,
			deleteItemFromDatabase: deleteItemFromDatabase,
			updateFieldsInDatabase: updateFieldsInDatabase,
			deleteM2MItemFromDatabase: deleteM2MItemFromDatabase,
			pad2: pad2,


			updateFieldsInDatabasePromise: updateFieldsInDatabasePromise,
			getItemsFromDatabasePromise: getItemsFromDatabasePromise,
			getItemFromDatabasePromise: getItemFromDatabasePromise,
			createItemInDatabasePromise: createItemInDatabasePromise,
			updateItemInDatabasePromise: updateItemInDatabasePromise,
			deleteItemFromDatabasePromise: deleteItemFromDatabasePromise
			};
	}


	//----------------END PUBLIC METHODS----------------


} () );



//
//    /** Turns a querystring into an object of key/value pairs.
//    Required Argument:
//    querystring - the querystring to be parsed
//    Optional Arguments:
//    strip_leading_question_mark - (boolean, optional) if set
//    to false, any leading question mark is not removed.
//    decodeKeys - (boolean, optional) if set to false,
//    keys are passed through [decodeURIComponent][]; defaults
//    to true
//    decodeValues - (boolean, optional) if set to false, values
//    are passed through [decodeURIComponent][]; defaults to true
//*/
//parse_query_string: function (querystring,
//                              strip_leading_question_mark,
//                              decodeKeys,
//                              decodeValues) {
//    var vars, object, i, length;
//    if (typeof querystring === "undefined") {
//        throw new TypeError(
//            "querystring is a required argument."
//        );
//    }
//    if (
//        (typeof decodeKeys === "undefined") ||
//            (decodeKeys === null)
//    ) {
//        decodeKeys = true;
//    }
//    if (
//        (typeof decodeValues === "undefined") ||
//            (decodeValues === null)
//    ) {
//        decodeValues = true;
//    }
//    if (typeof strip_leading_question_mark === "undefined") {
//        strip_leading_question_mark = true;
//    }
//    if (
//        strip_leading_question_mark &&
//            querystring.charAt(0) === '?'
//    ) {
//        querystring = querystring.substring(1);
//    }
//    vars = querystring.split(/[&;]/);
//    object = {};
//    if (!vars.length) {
//        return object;
//    }
//
//    vars.map(function (val) {
//        var index, value, keys, obj;
//        index = val.indexOf('=') + 1;
//        value = index ? val.substr(index) : '';
//        keys = index ? val.substr(
//            0,
//            index - 1
//        ).match(
//                /([A-Za-z0-9_\-\.\,\?\$\(\)\*\+~\/@\ ]+|(\B)(?=\]))/g
//        ) : [val];
//        obj = object;
//        if (!keys) {
//            return;
//        }
//        if (decodeValues) {
//            value = decodeURIComponent(value);
//        }
//        if (MAG.TYPES.is_string(value)) {
//            if (value.indexOf('JSON:') === 0) {
//                value = value.substr(5);
//                value = JSON.parse(value);
//            }
//        }
//        keys.map(function (key, i) {
//            var current;
//            if (decodeKeys) {
//                key = decodeURIComponent(key);
//            }
//            current = obj[key];
//
//            if (i < keys.length - 1) {
//                obj = obj[key] = current || {};
//            } else if (MAG.TYPES.is_array(current)) {
//                current.push(value);
//            } else {
//                if (typeof current === 'undefined') {
//                    obj[key] = value;
//                } else {
//                    obj[key] = [current, value];
//                }
//            }
//        });
//    });
//
//    return object;
//},
//
///** Returns the current query arguments as an object of key,
//value pairs. */
//get_current_query: function () {
//if (
//    window.location.search === "" ||
//        window.location.search === "?"
//) {
//    return {};
//}
//return MAG.URL.parse_query_string(window.location.search);
//},
