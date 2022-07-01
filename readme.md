# HeyseForms

## Replicating

```
pip install -r requirements.txt
python src/main.py
```

## Technical

### HTML Endpoints

#### GET `/`

HTTP 308 Permanent Redirect to `/home`

#### GET `/home`

Landing page

#### GET `/homeadmin`

Landing page (Admin)

#### GET `/settings`

Settings page

#### GET `/settingsadmin`

Settings page (Admin)

#### GET `/responses`

HTTP 308 Permanent Redirect to `/home`

#### GET `/responses/{uniqname}`

HTTP 307 Temporary Redirect to `/responses/{uniqname}/{entry}` where `entry` is the latest submitted entry

#### GET `/responses/{uniqname}/{entry}`

Displays a particular form response or a 404 type page if not found

### API Endpoints

TODO. These are called when settings are tweaked.
