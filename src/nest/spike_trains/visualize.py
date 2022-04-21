from pylab import *
import scipy.io as sio              
# %matplotlib inline
rcParams['figure.figsize']=(12,3)  # Change the default figure size

data = sio.loadmat('matfiles/08_spikes-1.mat')       # Load the spike train data
SpikesLow = data['SpikesLow'][0]         # ... and get the spike times for low-light condition.

ISIsLow = diff(SpikesLow)             # Compute ISIs in the low-light condition
                                         # Fit a statistical model to the ISIs.
bins = arange(0, .5, 0.001)           # Define 1 ms bins.
Nlow = len(ISIsLow)                      # Length of low-light condition.
mu = ISIsLow.mean()                      # Mean of inverse Gaussian
lbda = 1 / (1 / ISIsLow - 1 / mu).mean()    # ... and shape parameter
model = (                                   # ... to create the model.
    sqrt(lbda / 2 / pi / bins ** 3) * 
    exp(-lbda * (bins - mu) ** 2 / 2 / mu ** 2 / bins) * 0.001
)
model[0] = 0                             # Numerator to 0 faster than denominator.

subplot(121)                         # Plot the data and the model,
counts, _ = histogram(ISIsLow, bins)  # Compute histogram,
prob = counts / len(ISIsLow)             # ... convert to probability,
bar(bins[:-1], prob, width=1e-3)     # ... and plot probability.
plot(bins, model, 'b')                   # Plot the model.
xlim([0, 0.2])                       # xlim from 0 to 200 ms.
xlabel('ISI [s]')                        # Label the axes.
ylabel('Probability')

subplot(122)                         # Plot the KS plot
FmodLow = cumsum(model[:-1])          # Define the model CDF,
FempLow = cumsum(prob)                # ... and define empirical CDF,
plot(FmodLow, FempLow)                   # ... plot model vs empirical CDF,
plot([0, 1], arange(2) + 1.36 / sqrt(Nlow),'k:')  # ... upper confidence bound,
plot([0, 1], arange(2) - 1.36 / sqrt(Nlow),'k:')  # ... lower confidence bound,
axis([0, 1, 0, 1])                   # ... set the axes ranges,
xlabel('Model CDF')                      # ... and label the axes.
ylabel('Empirical CDF')

print(data)
# show()