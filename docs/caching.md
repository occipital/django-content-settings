# Caching

Local thread contains py values for all of the settings in the system. Py value is a parsed raw value (one than in the DB).

So every time when you use setting in code, you do not get raw value from the DB, parse it and return it. You already have a parsed value in the local thread.

And the cache trigger class is responsable for updating py values when those are updated in the DB.

The default trigger class is `content_settings.cache_triggers.VersionChecksum` (name is stored in [`CONTENT_SETTINGS_CACHE_TRIGGER`](settings.md#content_settings_cache_trigger)).

The way it works:

* during the first run, the checksum is calculated for all the values from the DB and saved to the cache backend
* the cache key is calculated based on the current versions of all of the settings.
* if the DB values are changed it saves the new checksum under the same cache key (so only instances with the same configuration will see the change)
* if the checksum is changed comparing to the checksum in the local storage

See also [`content_settings.cache_triggers`](source.md#cache_triggers)

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

See also [`content_setting.caching`](source.md#caching)

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)