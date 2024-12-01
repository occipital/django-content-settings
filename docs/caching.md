# Caching

There are two storages of raw data - DB and thread data. The cache is using to signal that it is time for local cache to be updated.

During the first run, a checksum is calculated for all registered variables. The checksum will be used as a cash key that signalise that value is is updated and need to be updated from DB.

The value from DB is taken only when at least one setting in the thread was requested. In that case we request data from the DB only when it is requred.

When at least one setting was requested - all of the raw values are fetched as saved in the thread. In that case all of the settings are consistent.

Raw data of a setting converts to py object of teh setting only when the setting was requested. In that case system do not spend too much time to convert all of the raw data. And since raw data can only be converted to on py object - it is ok to be converted any time.

Every request system checks the cache to check is the checksum value was changed. And if it is changed - system marks the thread data as not populated.

When the system repopulates (the setting is requested again after being unpopulated) - it updates all of the raw values but py object will be invalidated only in case of raw value was changed.

The cache trigger class is responsible for updating Py values when corresponding database values are updated. 

The default trigger class is `content_settings.cache_triggers.VersionChecksum`, and its name is stored in [`CONTENT_SETTINGS_CACHE_TRIGGER`](settings.md#content_settings_cache_trigger).

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
