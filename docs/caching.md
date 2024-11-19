# Caching

The local thread contains Py values for all settings in the system. A Py value is a parsed version of the raw value (stored in the database). 

When you use a setting in your code, you do not fetch the raw value from the database, parse it, and then return it. Instead, a parsed value is already stored in the local thread, ensuring efficient access.

The cache trigger class is responsible for updating Py values when corresponding database values are updated. 

The default trigger class is `content_settings.cache_triggers.VersionChecksum`, and its name is stored in [`CONTENT_SETTINGS_CACHE_TRIGGER`](settings.md#content_settings_cache_trigger).

### How It Works:

1. During the first run, a checksum is calculated for all the values in the database and saved to the cache backend.
2. A cache key is calculated based on the current versions of all settings.
3. If database values are changed, a new checksum is saved under the same cache key. Only instances with the same configuration will notice the change.
4. If the checksum differs from the one stored in the local cache, Py values are updated accordingly.

See also [`content_settings.cache_triggers`](source.md#cache_triggers).

---

## Raw to Py to Value

The journey from a database raw value to the setting's final returned value (`settings` attribute) consists of two stages:

1. **Creating a Py Object from the Raw Value**:
   - The process of retrieving an updated value includes converting the raw value into a Py object.
   
2. **Using the `give` Function**:
   - The `give` function of the type class converts the Py object into the attribute's final value.

### Behavior for Different Types:
- **Simple Types**: 
   - The `give` function directly returns the Py object.
   
- **Complex Types**:
   - The `give` function can:
     - Utilize the context in which the attribute is used.
     - Apply suffixes of the attribute to modify the returned value.

---

## When Is the Checksum Validated?

The checksum is checked in the following scenarios:

- **At the Beginning of a Request**:
  - Triggered by `signals.check_update_for_request`.
  
- **Before a Celery Task (if Celery is available)**:
  - Triggered by `signals.check_update_for_celery`.
  
- **Before a Huey Task (if Huey is available)**:
  - Triggered by `signals.check_update_for_huey`.

See also [`content_settings.caching`](source.md#caching).

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)
