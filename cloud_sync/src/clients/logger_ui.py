from logging import Logger


class LoggerUi:
    def __init__(self, logger: Logger):
        self._logger = logger

    def output(self, message):
        self._logger.info(message)

    def message(self, message):
        print('=== ' + message)

    def confirm(self, message, default):
        """Handy helper function to ask a yes/no question.

        A blank line returns the default, and answering
        y/yes or n/no returns True or False.

        Retry on unrecognized answer.

        Special answers:
        - q or quit exits the program
        - p or pdb invokes the debugger
        """
        if default:
            message += ' [Y/n] '
        else:
            message += ' [N/y] '
        while True:
            self._logger.debug('--')
            user_answer = input(message)
            answer = user_answer.strip().lower() if user_answer else None

            if not answer:
                return default
            if answer in ('y', 'yes'):
                return True
            if answer in ('n', 'no'):
                return False
            if answer in ('q', 'quit'):
                self._logger.warning('Exit')
                raise SystemExit(0)
            if answer in ('p', 'pdb'):
                import pdb
                pdb.set_trace()
            self._logger.debug('Please answer YES or NO.')
