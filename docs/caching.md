# Caching

There are two storage mechanisms for raw data: the database (DB) and thread-local storage. The cache is used to signal when the local cache needs to be updated.

During the first run, a checksum is calculated for all registered variables. This checksum acts as a cache key that signals when a value has been updated and needs to be refreshed from the DB.

Values from the DB are retrieved only when at least one setting in the thread is requested. In this case, data is fetched from the DB only when required.

Once at least one setting is requested, all raw values are fetched and saved in the thread-local storage. This ensures that all settings remain consistent.

Raw data for a setting is converted to a Python object only when the setting is requested. This avoids unnecessary processing of all raw data. Since raw data can be converted to a Python object at any time, this approach is efficient.

For every request, the system checks the cache to verify if the checksum value has changed. If it has, the thread-local data is marked as unpopulated.

When the system repopulates (i.e., a setting is requested again after being marked unpopulated), it updates all raw values. However, Python objects are invalidated only if the corresponding raw value has changed.

The cache trigger class is responsible for updating Python objects when the corresponding database values are updated.

The default trigger class is `content_settings.cache_triggers.VersionChecksum`, and its name is stored in [`CONTENT_SETTINGS_CACHE_TRIGGER`](settings.md#content_settings_cache_trigger).

---

## Raw to Python to Value

The journey from a database raw value to the setting's final returned value (`settings` attribute) consists of two stages:

1. **Creating a Python Object from the Raw Value**:
   - Retrieving an updated value involves converting the raw value into a Python object.
   
2. **Using the `give` Function**:
   - The `give` function of the type class converts the Python object into the attribute's final value.

### Behavior for Different Types:
- **Simple Types**: 
   - The `give` function directly returns the Python object.
   
- **Complex Types**:
   - The `give` function can:
     - Utilize the context in which the attribute is used.
     - Apply suffixes of the attribute to modify the returned value.

---

## When Is the Checksum Validated?

The checksum is validated in the following scenarios:

- **At the Beginning of a Request**:
  - Triggered by `signals.check_update_for_request`.
  
- **Before a Celery Task (if Celery is available)**:
  - Triggered by `signals.check_update_for_celery`.
  
- **Before a Huey Task (if Huey is available)**:
  - Triggered by `signals.check_update_for_huey`.

---

## Precached Python Values

*Experimental Feature*

The system allows all Python objects to be precached for each thread at the time the thread starts (e.g., when the DB connection is initialized).

To activate this feature, set: `CONTENT_SETTINGS_PRECACHED_PY_VALUES = True`

Note: This feature might cause issues if a new thread is started for every request.

See also [`content_settings.caching`](source.md#caching).

[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)