// ----------------------------------------------------------------------------
// -                        Open3D: www.open3d.org                            -
// ----------------------------------------------------------------------------
// The MIT License (MIT)
//
// Copyright (c) 2018 www.open3d.org
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
// IN THE SOFTWARE.
// ----------------------------------------------------------------------------

#pragma once

#include <Eigen/Core>
#include <string>
#include <unordered_map>
#include <unordered_set>

#include "open3d/core/Tensor.h"
#include "open3d/core/TensorList.h"
#include "open3d/core/hashmap/Hashmap.h"
#include "open3d/t/geometry/Geometry.h"
#include "open3d/t/geometry/Image.h"
#include "open3d/t/geometry/PointCloud.h"
#include "open3d/t/geometry/TensorListMap.h"

namespace open3d {
namespace t {
namespace geometry {

/// Scalable voxel grid specialized for TSDF integration.
/// The 3D space is organized in such a way:
/// Space is first coarsely divided into \blocks that can be indexed by 3D
/// coordinates.
/// Each \block is then further divided into \voxels as a Tensor of shape
/// (resolution, resolution, resolution, channel).
/// For pure geometric TSDF voxels, channel = 2 (TSDF + weight).
/// For colored TSDF voxels, channel = 5 (TSDF + weight + color).
/// Users may specialize their own channels that can be reinterpreted from the
/// internal Tensor.
class TSDFVoxelGrid {
public:
    /// \brief Default Constructor.
    TSDFVoxelGrid(std::unordered_map<std::string, int> attr_channel_map =
                          {{"tsdf", 1}, {"weight", 1}},
                  float voxel_size = 0.01,       /* in meter */
                  float sdf_trunc = 0.03,        /*  in meter  */
                  int64_t block_resolution = 16, /*  block Tensor resolution  */
                  int64_t block_count = 1000,
                  const core::Device &device = core::Device("CPU:0"));

    ~TSDFVoxelGrid(){};

    /// Depth-only integration
    void Integrate(const Image &depth,
                   const core::Tensor &intrinsics,
                   const core::Tensor &extrinsics,
                   double depth_scale = 1000.0);

    /// Extract point cloud near iso-surfaces
    PointCloud ExtractSurface();

protected:
    std::unordered_map<std::string, int> attr_channel_map_;

    /// Return (active_entries, 27) with \addrs and \masks for radius (3)
    /// neighbor entries. Currently we preserve redundancy without compressing /
    /// reduction.
    std::pair<core::Tensor, core::Tensor> BufferRadiusNeighbors(
            const core::Tensor &active_addrs);

    float voxel_size_;
    float sdf_trunc_;

    int64_t block_resolution_;
    int64_t block_count_;

    core::Device device_ = core::Device("CPU:0");

    std::shared_ptr<core::Hashmap> block_hashmap_;
};
}  // namespace geometry
}  // namespace t
}  // namespace open3d
