def serialize_object(obj):
  # owner id has to be serialized to string because when it is passed as bson.ObjectId,
  # then such error is thrown: "pydantic_core._pydantic_core.PydanticSerializationError:
  # Unable to serialize unknown type: <class 'bson.objectid.ObjectId'>""

  error = obj.get('error')
  if error is None:
    print('isNone')
    return obj

  new_error_arr = []

  for e in error:
    input_dict = e.get("input")
    if input_dict is None:
      new_error_arr.append(e)
    else:
      input_dict = dict(input_dict)
      ownerId = input_dict.get('ownerId')
      if ownerId is None:
        new_error_arr.append(e)
      else:
        input_dict['ownerId'] = str(input_dict['ownerId'])
        e['input'] = input_dict
        new_error_arr.append(e)

  obj['error'] = new_error_arr
  return obj