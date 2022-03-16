import nest
import numpy
import matplotlib.pyplot as plt

def extract_events(data, time=None, sel=None):
    """
    Extracts all events within a given time interval or are from a
    given set of neurons.
    - data is a matrix such that
      data[:,0] is a vector of all gids and
      data[:,1] a vector with the corresponding time stamps.
    - time is a list with at most two entries such that
      time=[t_max] extracts all events with t< t_max
      time=[t_min, t_max] extracts all events with t_min <= t < t_max
    - sel is a list of gids such that
      sel=[gid1, ... , gidn] extracts all events from these gids.
      All others are discarded.
    Both time and sel may be used at the same time such that all
    events are extracted for which both conditions are true.
    """

    val = []

    if time:
        t_max = time[-1]
        if len(time) > 1:
            t_min = time[0]
        else:
            t_min = 0

    for v in data:
        t = v[1]
        gid = v[0]
        if time and (t < t_min or t >= t_max):
            continue
        if not sel or gid in sel:
            val.append(v)

    return numpy.array(val)


def from_data(ax, data, color_marker, color_bar, color_edge, title, hist, hist_binwidth, sel=None):
    """
    Plot raster from data array
    """

    ts = data[:, 1]
    d = extract_events(data, sel=sel)
    ts1 = d[:, 1]
    gids = d[:, 0]

    print('data', data)
    print('d', d)

    return _make_plot(ax, ts, ts1, gids, data[:, 0], hist, hist_binwidth, color_marker, color_bar, color_edge, title)


def from_file(fname, title, color_marker, color_bar, color_edge, hist, hist_binwidth):
    """
    Plot raster from file
    """

    if nest.is_iterable(fname):
        data = None
        for f in fname:
            if data is None:
                data = numpy.loadtxt(f)
            else:
                data = numpy.concatenate((data, numpy.loadtxt(f)))
    else:
        data = numpy.loadtxt(fname)

    return from_data(data, title, color_marker, color_bar, color_edge, hist, hist_binwidth)


def from_device(ax, detec, title=None, color_marker='.k', color_bar='blue', color_edge='black', hist=False, hist_binwidth=5.0, plot_lid=False, xlabel=None, ylabel=None):
    """
    Plot raster from spike detector
    """

    if not nest.GetStatus(detec)[0]["model"] == "spike_detector":
        raise nest.NESTError("Please provide a spike_detector.")

    if nest.GetStatus(detec, "to_memory")[0]:

        times, senders = _from_memory(detec)

        if not len(times):
            raise nest.NESTError("No events recorded!")

        if plot_lid:
            # ? questo cosa fa?
            senders = [nest.GetLID([x]) for x in senders]

        if title is None:
            title = "Raster plot from device '%i'" % detec[0]

        if nest.GetStatus(detec)[0]["time_in_steps"]:
            xlabel = "Steps"
        else:
            xlabel = "Time (ms)"

        return _make_plot(ax, times, times, senders, senders, hist, hist_binwidth, color_marker, color_bar, color_edge, title, xlabel)

    elif nest.GetStatus(detec, "to_file")[0]:
        fname = nest.GetStatus(detec, "filenames")[0]
        return from_file(fname, title, hist, hist_binwidth, color_marker, color_bar, color_edge)

    else:
        raise nest.NESTError("No data to plot. Make sure that either to_memory or to_file are set.")

def _from_memory(detec):
    """
    Return times and senders from detector
    """
    ev = nest.GetStatus(detec, "events")[0]
    return ev["times"], ev["senders"]

def _make_plot(ax, times, times1, gids, neurons, hist, hist_binwidth, color_marker, color_bar, color_edge, title=None, xlabel=None, ylabel=None, threshold=None):
    """
    Generic plotting routine that constructs a raster plot along with
    an optional histogram (common part in all routines above)
    """

    if xlabel is None:
        xlabel = "Time (ms)"

    ylabel = "Neuron ID"

    if hist:
        
        plot = ax.eventplot(times1, gids)
        labels = ax.get_xticklabels()
        print('times: ', times)
        print('times1: ', times1)
        print('gids: ', gids)
        print('labels: ', labels)
        # ax.setp(labels, rotation=45, horizontalalignment='right')
        if xlabel: ax.set_xlabel(xlabel)
        if ylabel: ax.set_ylabel(ylabel)
        if title: ax.set_title(title)
        # if (threshold):
            # * Add threshold line here
            # plot.axhline(threshold, ls='--', color='r')
        # * in case we needed to break down x labels into major values
        # plot.set_xticks([0, 25e3, 50e3, 75e3, 100e3, 125e3])

        # ax1 = pylab.axes([0.1, 0.3, 0.85, 0.6])
        # plotid = pylab.plot(times1, gids, color_marker)
        # pylab.ylabel(ylabel)
        # pylab.xticks([])
        # xlim = pylab.xlim()

        # pylab.axes([0.1, 0.1, 0.85, 0.17])
        # t_bins = numpy.arange(numpy.amin(times), numpy.amax(times), float(hist_binwidth))
        # n, bins = _histogram(times, bins=t_bins)
        # num_neurons = len(numpy.unique(neurons))
        # heights = 1000 * n / (hist_binwidth * num_neurons)
        # pylab.bar(t_bins, heights, width=hist_binwidth, color=color_bar, edgecolor=color_edge)
        # pylab.yticks([int(x) for x in numpy.linspace(0.0, int(max(heights) * 1.1) + 5, 4)])
        # pylab.ylabel("Rate (Hz)")
        # pylab.xlabel(xlabel)
        # pylab.xlim(xlim)
        # pylab.axes(ax1)
    # else:
    #     plotid = pylab.plot(times1, gids, color_marker)
    #     pylab.xlabel(xlabel)
    #     pylab.ylabel(ylabel)
    
    return plot


def _histogram(a, bins=10, bin_range=None, normed=False):
    from numpy import asarray, iterable, linspace, sort, concatenate

    a = asarray(a).ravel()

    if bin_range is not None:
        mn, mx = bin_range
        if mn > mx:
            raise ValueError("max must be larger than min in range parameter")

    if not iterable(bins):
        if bin_range is None:
            bin_range = (a.min(), a.max())
        mn, mx = [mi + 0.0 for mi in bin_range]
        if mn == mx:
            mn -= 0.5
            mx += 0.5
        bins = linspace(mn, mx, bins, endpoint=False)
    else:
        if (bins[1:] - bins[:-1] < 0).any():
            raise ValueError("bins must increase monotonically")

    # best block size probably depends on processor cache size
    block = 65536
    n = sort(a[:block]).searchsorted(bins)
    for i in range(block, a.size, block):
        n += sort(a[i:i + block]).searchsorted(bins)
    n = concatenate([n, [len(a)]])
    n = n[1:] - n[:-1]

    if normed:
        db = bins[1] - bins[0]
        return 1.0 / (a.size * db) * n, bins
    else:
        return n, bins

def show():
    """
    Call pylab.show() to show all figures and enter the GUI main loop.
    Python will block until all figure windows are closed again.
    You should call this function only once at the end of a script.

    See also: http://matplotlib.sourceforge.net/faq/howto_faq.html#use-show
    """

    pylab.show()