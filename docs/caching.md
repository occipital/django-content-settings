[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Caching

This is a very important part of content settings since it solves two main problems:

* Consistency within a call - cache contains DB state as checksum and checksum check is always at the beginning of the call to avoid taking content settings updates from different DB transactions 
* Unlimited value complexity - updating value from DB includes getting raw text value from DB, converting it into a py object, and storing py object in a local thread.

## Procedure of update py value.

* user changes the value in Django admin (validation of the values passed correctly)
* make a record in history with the source of the update
* after data is committed, recalculate the checksum and save it in the cache
* when the call begins (e.g., start of the request, start of celery task), the system checks if the current checksum is different from one from the cache
* if the value is different, check the DB raw values and recalculate the py-object for those that changed
* the new py-objects, as well as updated raw values, are stored in the local thread
* the updated checksum is stored in the local thread

## Raw to Py to Value

A way from the value from DB (raw value) to the setting value (returned be `settings` attribute) consists of two stages:

* creating a Py object from raw value - the process of receiving updated value also includes converting this value into a Py object.
* function `give` of the type class is used for getting the attribute of the value by converting py object into the result of the attribute call.

For simple types `give` function simply returns a py object, but for moving complex types you can:

* use the context of where the attribute was used
* use suffixes of the attribute

## Calls or when we check the checksum

* at the beginning of request `signals.check_update_for_request`
* before the celery task (if the celery import is possible) `signals.check_update_for_celery`
* before the huey task (if the huey import is possible) `signals.check_update_for_huey`
