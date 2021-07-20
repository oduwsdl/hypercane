import logging

DEFAULT_LOGFILE = "./creating-sample.log"

from hypercane.args.sample import sample_parser

if __name__ == '__main__':

    args = sample_parser.parse_args()

    # set up logging for the rest of the system
    logger = logging.getLogger(__name__)
    logging.basicConfig( 
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        level=logging.INFO,
        filename=DEFAULT_LOGFILE)

    start_message = "Beginning Hypercane sample action"

    print(start_message)
    logger.info(start_message)

    end_message = "Done with Hypercane sample action. Output is available at {}. THE END.".format(args.output_filename)

    logger.info(end_message)
    print(end_message)
