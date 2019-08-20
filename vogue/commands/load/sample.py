import logging
import click
from vogue.load.sample import load_one, load_all, load_recent, load_one_dry, load_all_dry
from flask.cli import with_appcontext, current_app
from datetime import datetime


from genologics.entities import Sample


LOG = logging.getLogger(__name__)

@click.command("sample", short_help = "load sample/samples into db.")
@click.option('-s', '--sample-lims-id', 
                help = 'Input sample lims id')
@click.option('-a', '--all_samples', is_flag = True, 
                help = 'Loads all lims samples if no other options are selected')
@click.option('-f', '--load-from', 
                help = 'load from this sample lims id. Use if load all broke. Start where it ended')
@click.option('-d', '--days', 
                help = 'Update only samples updated in the latest number of days')
@click.option('--dry', is_flag = True, 
                help = 'Load from sample or not. (dry-run)')

@with_appcontext
def sample(sample_lims_id, all_samples, load_from, days, dry):
    """Read and load lims data for one sample, all samples or the most recently updated samples."""
    
    if not current_app.lims:
        LOG.warning("Lims connection failed.")
        raise click.Abort()

    lims = current_app.lims
        
    if days:
        try:
            some_days_ago = date.today() - timedelta(days=days) 
            the_date = some_days_ago.strftime("%Y-%m-%dT00:00:00Z")
        except Exception as err:
            LOG.error(err)
            raise click.Abort()
        load_recent(current_app.adapter,lims=lims, the_date)

    if all_samples:
        if dry:
            load_all_dry()
        else:
            load_all(current_app.adapter, lims=lims, start_sample=load_from)
    else:
        lims_sample = Sample(lims, id = sample_lims_id)
        if not lims_sample:
            LOG.critical("The sample does not exist in the database in the LIMS database.")
            raise SyntaxError()
        if dry:
            load_one_dry(lims_sample)
        else:
            load_one(current_app.adapter, lims_sample , lims=lims)



