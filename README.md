## Python Laravel Queue

Queue sync between Python and Laravel using Redis driver. You can process jobs dispatched from Laravel in Python.

**NOTE: This package is in beta and only Redis is supported currently. Production usage is not recommended until stable release.**

In the 1.0.0 stable version these implementations are planned:

- Auto-discovery jobs in both Laravel and Python.
- Auto-configuration by reading Laravel config in Python side.
- More clean API.
- Supporting more queue drivers.

### Install

```bash
pip install python-laravel-queue
```

### Usage

- Listen for jobs on Python:

```python
from python_laravel_queue import Queue as PlQueue
from redis import Redis

r = Redis(host='localhost', port=6379, db=0)
queue_python = PlQueue(r, queue='python')

@queue_python.handler
def handle(data):
    name = data['name'] # job name
    data = data['data'] # job data
    print('TEST: ' + data['a'] + ' ' + data['b'] + ' ' + data['c'])

queue_python.listen()
```

- Sending jobs from Laravel :

```php
<?php
$job = new \App\Jobs\TestJob('hi','send to','python');
dispatch($job)->onQueue('python');
```

- Schedule a job to be run in Laravel from Python:

```python
from python_laravel_queue import Queue as PlQueue
from redis import Redis

r = Redis(host='localhost', port=6379, db=0)
queue_laravel = PlQueue(r, queue='laravel')
queue_laravel.push('App\\Jobs\\TestJob', {'a': 'hello', 'b': 'send to', 'c': 'laravel'})

```

**TestJob** in Laravel:

```php
<?php

namespace App\Jobs;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;

class TestJob extends Job implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $a, $b, $c;

    /**
     * Create a new job instance.
     *
     * @return void
     */
    public function __construct ($a, $b, $c) {
        $this->a = $a;
        $this->b = $b;
        $this->c = $c;
    }

    public function handle () {
        Log::info('TEST: ' . $this->a . ' '. $this->b . ' ' . $this->c);
    }
}

```

- You need to :listen (or :work) the preferred queue name above to handle data sent from Python in Laravel.

```bash
php artisan queue:listen --queue=laravel
```
