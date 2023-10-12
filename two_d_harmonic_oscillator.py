import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.animation import FuncAnimation

class Sim_Params:
    def __init__(self,
                 xmax: float,
                 res: int,
                 dt: float,
                 timesteps: int,
                 wf_offset: float,
                 V_offset: tuple[float, float]) -> None:
        # constants
        self.m = 1
        self.omega = 1
        self.hbar = 1
        # user values
        self.xmax = xmax
        self.res = res
        self.dt = dt
        self.timesteps = timesteps
        self.wf_offset = wf_offset
        self.V_offset = V_offset
        
        

class Simulator:
    def __init__(self,
                 params: Sim_Params) -> None:
        self.params = params
        # calculate step sizes
        x_length = 2 * params.xmax
        self.dx = x_length / params.res
        self.dp = params.hbar * (2 * np.pi / x_length)
        # create the simulation space
        self.__x_space = np.arange(-params.xmax + (params.xmax / params.res), params.xmax, self.dx)
        self.__y_space = self.__x_space.copy()
        self.__X, self.__Y = np.meshgrid(self.__x_space, self.__y_space)
        self.__px_space = np.concatenate((np.arange(0, params.res / 2), np.arange(-params.res / 2, 0))) * self.dp
        self.__py_space = self.__px_space.copy()
        self.__Px, self.__Py = np.meshgrid(self.__px_space, self.__py_space)

        self.__V = 0.5 * params.m * params.omega**2 * ((self.__X - params.V_offset[0])**2 + (self.__Y - params.V_offset[1])**2)
        self.__initialize()
        self.__x_half_step_operator = np.exp(0.5 * (-1j * self.__V * params.dt))
        self.__p_full_step_operator = np.exp(-1j * (self.__Px**2 + self.__Py**2) * params.dt / (2 * params.m))

    
    def __initialize(self) -> np.ndarray[complex]:
        self.__current_time = 0
        # initilize wfc
        self.wfc = np.exp(-((self.__X - self.params.wf_offset[0])**2 + (self.__Y - self.params.wf_offset[1])**2) / 2, dtype=complex)


    def __probability_density(self):
        return np.abs(self.wfc)**2
    
    def plot_current_state(self):
        fig: Figure
        ax: Axes
        ax2: Axes
        fig, ax = plt.subplots()
        density = self.__probability_density()
        pcm = ax.pcolormesh(self.__X, self.__Y, density.real, shading='auto', cmap='viridis')
        cbar = fig.colorbar(pcm, ax=ax, label='Density')
        cbar.ax.set_ylabel('Density')
        ax2 = ax.twinx()
        ax2.contour(self.__X, self.__Y, self.__V, colors='r', levels=10)
        ax.set_title(f'Time: {self.__current_time:.2f}')
        return (fig, ax, ax2)


    def split_evolve(self):
        self.wfc *= self.__x_half_step_operator
        self.wfc = np.fft.fft2(self.wfc)
        self.wfc *= self.__p_full_step_operator
        self.wfc = np.fft.ifft2(self.wfc)
        self.wfc *= self.__x_half_step_operator
        self.__current_time += self.params.dt


    def simulate(self):
        fig, ax, ax2 = self.plot_current_state()

        def update(i):
            if i == 0:
                return
            self.split_evolve()
            density = self.__probability_density()
            pcm = ax.get_children()[0]
            pcm.set_array(density.real.ravel())
            ax.set_title(f'Time: {self.__current_time:.2f}')

        ani = FuncAnimation(fig, update, frames=self.params.timesteps + 1)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        plt.close()  # Close the initial plot since it's not needed
        return ani
