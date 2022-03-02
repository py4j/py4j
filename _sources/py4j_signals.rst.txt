:mod:`py4j.signals` --- Py4J Signals API
========================================

.. module:: py4j.signals
  :synopsis: Basic signals implementation (listeners/events/observers).
.. moduleauthor:: Barthelemy Dagenais <barthelemy@infobart.com>

The :mod:`py4j.signals` module contains classes that enables the creation of
signals, i.e., events that can be sent to "receivers". A receiver must connect
to a signal beforehand and can optionally specify from which sender it should
receive signals.

Here is a full usage example:


.. code-block:: python

  # Declare a signal
  server_connection_stopped = Signal()
  """Signal sent when a Python (Callback) Server connection is stopped.

  Will supply the ``connection`` argument, an instance of CallbackConnection.

  The sender is the CallbackServer instance.
  """

  server = ...
  connection = ...

  # Create a receiver
  def on_connection_stopped(sender, **kwargs):
      connection = kwargs["connection"]
      # ...

  # Connect the receiver to the signal. Only signals sent from
  # server will be sent to on_connection_stopped.
  server_connection_stopped.connect(on_connection_stopped, sender=server)

  # Send a signal to the receivers. If one receiver raises an error,
  # the error is propagated back and other receivers won't receive the
  # signal.
  server_connection_stopped.send(sender=server, connection=connection)


Signal
------

.. autoclass:: py4j.signals.Signal
   :members:
   :undoc-members:
