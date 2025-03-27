import numpy as np
from scipy.stats import gaussian_kde

def marginal_distribution(data, variable_index, grid_points=100):
    """
    计算边缘分布函数。

    参数:
        data (numpy.ndarray): 数据集，形状为 (n_samples, n_features)。
        variable_index (int): 要计算边缘分布的变量索引。
        grid_points (int): 用于估计分布的网格点数量。

    返回:ss
        grid (numpy.ndarray): 网格点。
        marginal_pdf (numpy.ndarray): 边缘分布的概率密度值。
    """
    # 提取指定变量的数据
    variable_data = data[:, variable_index]
    
    # 使用核密度估计计算边缘分布
    kde = gaussian_kde(variable_data)
    
    # 创建网格点
    grid = np.linspace(variable_data.min(), variable_data.max(), grid_points)
    
    # 计算概率密度值
    marginal_pdf = kde(grid)
    
    return grid, marginal_pdf

# 示例数据
if __name__ == "__main__":
    # 生成二维正态分布数据
    mean = [0, 0]
    cov = [[1, 0.5], [0.5, 1]]
    data = np.random.multivariate_normal(mean, cov, size=1000)
    
    # 计算第一个变量的边缘分布
    grid, marginal_pdf = marginal_distribution(data, variable_index=0)
    
    # 可视化
    import matplotlib.pyplot as plt
    plt.plot(grid, marginal_pdf, label="边缘分布")
    plt.xlabel("变量值")
    plt.ylabel("概率密度")
    plt.title("边缘分布函数")
    plt.legend()
    plt.show()